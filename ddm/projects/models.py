from __future__ import annotations

import binascii
import datetime
import os
from collections import defaultdict
from pathlib import Path
from typing import Any

from Crypto.PublicKey import RSA
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Avg, Count, F, ImageField, QuerySet
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views.decorators.debug import sensitive_variables

from ddm.auth.models import ProjectAccessToken
from ddm.core.utils.misc import create_asciidigits_id
from ddm.core.utils.validators import validate_hex_color
from ddm.datadonation.models import DataDonation
from ddm.encryption.models import (
    Decryption,
    Encryption,
    unwrap_private_key,
    wrap_private_key,
)
from ddm.logging.models import EventLogEntry, ExceptionLogEntry
from ddm.participation.models import Participant


class ResearchProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ddm_research_profile",
    )
    active = models.BooleanField(default=True)
    created = models.DateTimeField("date registered", default=timezone.now)
    ignore_email_restriction = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.user.email


def project_header_dir_path(instance: DonationProject, filename: str) -> str:
    return f"project_{instance.pk}/headers/{filename}"


def generate_test_token() -> str:
    """Generates an unguessable test-mode token.

    Same mechanism as ProjectAccessToken.generate_key() (see
    ddm.auth.models) - a plain hex string rather than a UUID, for
    consistent, backend-portable storage.
    """
    return binascii.hexlify(os.urandom(20)).decode()


DEFAULT_PRIMARY_COLOR = "#007b74"
DEFAULT_BACKGROUND_COLOR = "#f8fafc"


class DonationProject(models.Model):
    url_id = models.SlugField(unique=True, max_length=8)

    # Basic information for internal organization.
    name = models.CharField(
        max_length=50,
        help_text=(
            "Project Name - for internal organisation only (can still be "
            "changed later)."
        ),
    )

    # Note: Value of "date_created" attribute must not be changed after
    # instance creation as it is used for en-/decryption.
    date_created = models.DateTimeField(default=timezone.now)
    owner = models.ForeignKey(
        "ResearchProfile",
        related_name="project_owner",
        on_delete=models.SET_NULL,
        null=True,
    )

    # Public information.
    contact_information = models.TextField(
        blank=False,
        verbose_name="Contact information",
        help_text=(
            "Please provide the contact information of the person responsible "
            "for the conduction of this study (Name, professional address, e-mail, "
            "tel, ...). The contact information will be accessible for "
            "participants during the data donation. The field is mandatory."
        ),
    )
    data_protection_statement = models.TextField(
        blank=False,
        verbose_name="Data Protection Statement",
        help_text=(
            "Please provide a data protection statement for your data donation "
            "collection. This should include the purpose for which the data is "
            "collected, how it will be stored, and who will have access to the "
            "data. The field is mandatory."
        ),
    )

    # Information affecting participation flow.
    slug = models.SlugField(
        unique=True,
        verbose_name="URL Identifier",
        help_text=mark_safe(
            "Identifier that is included in the URL through which participants "
            "can access the project "
            "(e.g, https://root.url/<b>my-url-identifier</b>). "
            "Can only contain letters, hyphens, numbers or underscores."
        ),
    )
    briefing_text = models.TextField(
        blank=False,
        verbose_name="Briefing Text",
        help_text=(
            "This text will be displayed to participants in the first step before "
            "beginning the data donation. Here, you should introduce your study, "
            "who is responsible for the study, provide a quick summary of what "
            "your participants will be asked to do in the next steps, etc."
        ),
    )
    briefing_consent_enabled = models.BooleanField(
        default=False,
        verbose_name="Briefing Consent Mandatory",
        help_text="Enable this option to obtain explicit consent from participant, "
        "that they want to start the study.",
    )
    briefing_consent_label_yes = models.CharField(max_length=255, blank=True)
    briefing_consent_label_no = models.CharField(max_length=255, blank=True)
    debriefing_text = models.TextField(
        blank=False,
        verbose_name="Debriefing Text",
        help_text="This text will be displayed to participants on the last page "
        "of the study (i.e., after the data donation and the questionnaire).",
    )

    # Appearance settings.
    show_project_title = models.BooleanField(default=False)
    img_header_left = ImageField(
        upload_to=project_header_dir_path,
        null=True,
        blank=True,
        verbose_name="Header Image Left",
    )
    img_header_right = ImageField(
        upload_to=project_header_dir_path,
        null=True,
        blank=True,
        verbose_name="Header Image Right",
    )
    primary_color = models.CharField(
        max_length=9,
        default=DEFAULT_PRIMARY_COLOR,
        validators=[validate_hex_color],
        verbose_name="Primary Color",
        help_text=(
            "Accent color used for buttons and highlights in the "
            "participation interface."
        ),
    )
    background_color = models.CharField(
        max_length=9,
        default=DEFAULT_BACKGROUND_COLOR,
        validators=[validate_hex_color],
        verbose_name="Background Color",
        help_text="Background color of the participation interface pages.",
    )

    # Access settings.
    public_key = models.BinaryField()
    super_secret = models.BooleanField(default=False)
    # Only ever set for standard (non-super_secret) projects created after
    # this field was introduced in v3 - holds that project's own randomly
    # generated RSA private key, encrypted at rest with a key derived from
    # settings.SECRET_KEY (see get_decryptor()). Always None for
    # super_secret projects (their key is never persisted, by design) and
    # for any project created before this field existed - those keep using
    # the legacy on-the-fly derivation from (secret, date_created).
    wrapped_private_key = models.BinaryField(null=True, blank=True, editable=False)

    # Redirect settings.
    redirect_enabled = models.BooleanField(
        default=False, verbose_name="Redirect enabled"
    )
    redirect_target = models.CharField(
        max_length=2000,
        blank=True,
        verbose_name="Redirect address",
        help_text=mark_safe(
            "Always include <i>https://</i> in the redirect address. "
            "If URL parameter extraction is enabled for this project, you can "
            "include the extracted URL parameters in the redirect address as follows: "
            '"https://redirect.me/?redirectpara=<b>{{participant.data.url_param.URLParameter}}</b>".'
        ),
    )

    # URL parameter extraction settings.
    url_parameter_enabled = models.BooleanField(
        default=False, verbose_name="URL parameter extraction enabled"
    )
    expected_url_parameters = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Expected URL parameter",
        help_text='Separate multiple parameters with a semikolon (";"). '
        "Semikolons are not allowed as part of the expected url parameters.",
    )

    active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Participants can only take part in a project if it is active.",
    )

    # Test mode. Project-scoped token that grants only "start a flagged test run
    # of this project" when passed as a `?test=` URL parameter on the
    # participation link.
    test_token = models.CharField(max_length=40, unique=True, editable=False)

    custom_uploader_translations = models.JSONField(
        blank=True,
        null=False,
        default=dict,
        help_text=(
            "Advanced option to overwrite default phrases and translations used "
            "in the data donation interface. Must be a dictionary with the "
            'locale shortcuts as keys (e.g., "de" or "en") associated to a '
            "dictionary holding the translations. Placeholders in overridden "
            'phrases must use simple "{param}" substitution, matching the '
            "defaults being overwritten; other formatting syntax (e.g., "
            "pluralization or linked messages) is not supported."
        ),
    )

    @sensitive_variables()
    def __init__(self, *args, **kwargs) -> None:
        self.secret_key = settings.SECRET_KEY
        if "secret_key" in kwargs:
            self.secret_key = kwargs["secret_key"]
            kwargs.pop("secret_key")
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

    @sensitive_variables()
    def save(self, *args, **kwargs) -> None:
        if not self.pk:
            if self.owner is None:
                msg = "DonationProject.owner cannot be null on create."
                raise ValidationError(msg)
        else:
            self.clean_file_on_reupload()

        if not self.public_key:
            if self.super_secret:
                self.public_key = Encryption.get_public_key(
                    self.secret, str(self.date_created)
                )
            else:
                self._generate_and_store_keypair()

        if not self.url_id:
            self.url_id = create_asciidigits_id(8)
            while DonationProject.objects.filter(url_id=self.url_id).exists():
                self.url_id = create_asciidigits_id(8)

        if not self.test_token:
            self.test_token = generate_test_token()

        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("ddm_projects:detail", args=[str(self.url_id)])

    def get_salt(self) -> str:
        return str(self.date_created)

    @sensitive_variables()
    def _generate_and_store_keypair(self) -> None:
        """
        Generates a fresh, independently random RSA keypair for this
        (standard, non-super_secret) project using pycryptodome's own
        secure default randomness, and stores the public key as-is
        plus the private key wrapped at rest with a key derived from
        settings.SECRET_KEY. Only ever called once, from save()'s
        "not self.public_key yet" branch.
        """
        key = RSA.generate(2048)
        self.public_key = key.publickey().export_key()
        self.wrapped_private_key = wrap_private_key(
            self.secret, key.export_key(format="DER")
        )

    @sensitive_variables()
    def get_decryptor(self, secret: str | None = None) -> Decryption:
        """
        Returns a Decryption instance for this project's data.

        - super_secret projects: derives the
          keypair on the fly from the given/default secret and this
          project's salt; nothing is ever persisted for these.
        - standard projects created after `wrapped_private_key` was
          introduced: unwraps the stored, randomly-generated private key
          using settings.SECRET_KEY - `secret` is ignored, there's nothing
          to re-derive from.
        - standard projects created before `wrapped_private_key` existed
          (it's still None/empty): falls back to the same legacy
          derivation as super_secret, keeping these projects' existing
          encrypted data decryptable exactly as before.
        """
        if not self.super_secret and self.wrapped_private_key:
            private_key_der = unwrap_private_key(
                self.secret_key, bytes(self.wrapped_private_key)
            )
            return Decryption(private_key=private_key_der)
        secret_key = secret if secret else self.secret_key
        return Decryption(secret_key, self.get_salt())

    @sensitive_variables()
    def verify_secret(self, secret: str) -> bool:
        """
        For super_secret projects: checks whether `secret` is able to
        correctly decrypt this project's data, without needing any
        already-encrypted data to test against (round-trips a known
        string through the project's own public key instead). Returns
        False on a wrong secret or any decryption error; never raises.
        """
        test_string = "Teststring"
        encrypted = Encryption(public=self.public_key).encrypt(test_string)
        try:
            decrypted = self.get_decryptor(secret=secret).decrypt(encrypted)
        except ValueError:
            return False
        return decrypted == test_string

    def clean_file_on_reupload(self) -> None:
        """
        Deletes previous file on model FileFields or ImageFields if a file
        is re-uploaded.
        """
        i = DonationProject.objects.get(pk=self.pk)
        for field in i._meta.fields:  # noqa: SLF001
            if field.get_internal_type() in ["FileField", "ImageField"]:
                old_file = getattr(i, field.name)
                new_file = getattr(self, field.name)
                if old_file and old_file != new_file:
                    try:
                        old_path = Path(old_file.path)
                        if old_path.is_file():
                            old_path.unlink()
                    except (ValueError, OSError):
                        pass

    @property
    def secret(self) -> str:
        return self.secret_key

    @secret.setter
    def secret(self, value: str) -> None:
        self.secret_key = value

    def delete(
        self,
        using: Any = None,  # noqa: ANN401
        keep_parents: bool = False,  # noqa: FBT002
    ) -> tuple[int, dict[str, int]]:
        # Manually delete related questions to circumvent foreign key integrity
        # problem caused by QuestionBase models inheriting from django-polymorphic.
        # (see https://github.com/django-polymorphic/django-polymorphic/issues/34#issuecomment-1027866872)
        for question in self.questionbase_set.all():
            question.delete()
        return super().delete(using, keep_parents)

    def get_statistics(self) -> dict[str, Any]:
        participants = Participant.objects.filter(project=self, is_test=False)
        donation_counts = DataDonation.objects.filter(
            project=self,
            participant__is_test=False,
            data_extraction_state=DataDonation.DataExtractionState.DATA_EXTRACTED,
        ).aggregate(
            n_donated_files=Count("id"),
            n_donations=Count("participant_id", distinct=True),
        )
        return {
            "n_started": participants.count(),
            "n_completed": participants.filter(completed=True).count(),
            "completion_rate": self.get_completion_rate(participants),
            "n_donations": donation_counts["n_donations"],
            "n_donated_files": donation_counts["n_donated_files"],
            "n_errors": ExceptionLogEntry.objects.filter(project=self)
            .exclude(participant__is_test=True)
            .count(),
            "average_time": self.get_average_completion_time(participants),
        }

    def get_blueprint_donation_status_counts(self) -> list[dict[str, Any]]:
        states = DataDonation.DataExtractionState
        tracked_states = [
            states.DATA_EXTRACTED,
            states.NO_DATA_EXTRACTED,
            states.NOT_ATTEMPTED,
            states.FAILED,
        ]
        rows = (
            DataDonation.objects.filter(project=self, participant__is_test=False)
            .values("blueprint_id", "data_extraction_state")
            .annotate(n=Count("id"))
        )
        by_blueprint: dict[int | None, dict[str, int]] = defaultdict(dict)
        for row in rows:
            by_blueprint[row["blueprint_id"]][row["data_extraction_state"]] = row["n"]

        results = []
        for blueprint in self.donationblueprint_set.all():
            state_counts = by_blueprint.get(blueprint.pk, {})
            results.append(
                {
                    "blueprint": blueprint,
                    "counts": [state_counts.get(s, 0) for s in tracked_states],
                    "n_other": sum(
                        v for k, v in state_counts.items() if k not in tracked_states
                    ),
                }
            )

        # Donations whose blueprint was deleted (DataDonation.blueprint is SET_NULL).
        orphaned = by_blueprint.get(None, {})
        if orphaned:
            results.append(
                {
                    "blueprint": None,
                    "counts": [orphaned.get(s, 0) for s in tracked_states],
                    "n_other": sum(
                        v for k, v in orphaned.items() if k not in tracked_states
                    ),
                }
            )
        return results

    def get_completion_rate(
        self, participants: QuerySet[Participant] | None = None
    ) -> float:
        if participants is None:
            participants = Participant.objects.filter(project=self, is_test=False)
        if participants.count() > 0:
            return participants.filter(completed=True).count() / participants.count()
        return 0

    def get_average_completion_time(
        self, participants: QuerySet[Participant] | None = None
    ) -> str:
        if participants is None:
            participants = Participant.objects.filter(project=self, is_test=False)
        return str(
            participants.filter(completed=True).aggregate(
                v=Avg(F("end_time") - F("start_time"))
            )["v"]
        ).split(".")[0]

    def get_expected_url_parameters(self) -> list[str]:
        return self.expected_url_parameters.split(";")

    @property
    def has_custom_theme(self) -> bool:
        """Whether either color differs from the built-in default.

        Used to skip rendering the participation interface's CSS color
        override entirely for un-customized projects.
        """
        return (
            self.primary_color != DEFAULT_PRIMARY_COLOR
            or self.background_color != DEFAULT_BACKGROUND_COLOR
        )

    @property
    def theme_version(self) -> str:
        """Cache-busting token derived from the current colors.

        Appended as a query parameter to the theme CSS URL so that changing
        either color changes the URL, forcing browsers/caches to fetch a
        fresh stylesheet instead of continuing to serve a cached one.
        """
        return f"{self.primary_color.lstrip('#')}{self.background_color.lstrip('#')}"

    def regenerate_test_token(self) -> None:
        """Rotates the test-mode token, cutting off anyone using the old link.

        Does not touch previously created test Participant rows - they
        remain in the database under the old (now unreachable) token.
        """
        self.test_token = generate_test_token()
        self.save(update_fields=["test_token"])
        EventLogEntry.objects.create(
            project=self, description="Test Link Token Regenerated"
        )

    def get_token(self) -> ProjectAccessToken | None:
        return ProjectAccessToken.objects.filter(project=self).first()

    def create_token(self, expiration_days: int | None = None) -> ProjectAccessToken:
        token = self.get_token()
        if token:
            token.delete()
        if expiration_days:
            expiration_date = timezone.now() + datetime.timedelta(days=expiration_days)
        else:
            expiration_date = None
        EventLogEntry.objects.create(
            project=self, description="New Access Token Created"
        )
        return ProjectAccessToken.objects.create(
            project=self, expiration_date=expiration_date
        )
