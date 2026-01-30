import json
from typing import Union

from django.db.models import QuerySet

from ddm.datadonation.models import FileUploader, DataDonation, DonationBlueprint
from ddm.logging.models import ExceptionLogEntry, ExceptionRaisers
from ddm.participation.models import Participant
from ddm.participation.serializers import (
    FilterConditionSerializer,
    FileUploaderSerializer,
    QuestionConfigSerializer,
)
from ddm.participation.utils import get_filter_config_id
from ddm.projects.models import DonationProject
from ddm.questionnaire.models import QuestionBase, FilterCondition, QuestionItem


class UploaderConfigService:
    """Service class to create uploader configuration to be passed to frontend."""

    @staticmethod
    def create_configs(
            file_uploaders: QuerySet[FileUploader],
            participant: Participant | None = None,
            return_as_string: bool = True
    ) -> str:
        """Create uploader configuration that can be passed to frontend.

        Returns the json configuration as string or as dict.

        see also: frontend/DDMUploader/src/types/UploaderConfig.ts
        """

        participant_data = participant.get_context_data() if participant else None
        context = {'participant_data': participant_data}

        uploader_configs = [
            FileUploaderSerializer(fu, context=context).data
            for fu in file_uploaders
        ]
        return json.dumps(uploader_configs) if return_as_string else uploader_configs


class QuestionnaireConfigService:
    """Service class to create questionnaire configuration to be passed to frontend."""

    def __init__(self, project: DonationProject, participant: Participant):
        """
        Args:
            project: The DonationProject instance for which to create the config.
            participant: The Participant instance for which to create the config.
        """
        self.project = project
        self.participant = participant
        self.questions: QuerySet[QuestionBase] = project.questionbase_set.all()

    def create_questionnaire_config(self, return_as_string: bool = True) -> list:
        """
        Returns a dictionary containing all information to render the
        questionnaire for a given participant that can be passed to the frontend
        questionnaire application.

        Args:
            return_as_string: Whether to return the config stringified with json.dumps()
                or as dict.

        Returns:
            list: A list in which each entry relates to one question and contains
                all information needed to render the question.
        """
        q_config = []
        questions = self.questions.order_by('page', 'index')
        for question in questions:
            if not question.is_general(): # means question associated to blueprint
                # Check if donation exists
                try:
                    donation = self.get_donation(question.blueprint)
                except DataDonation.DoesNotExist:
                    # Only show question to participant if donation was successful
                    continue

                donated_data = donation.get_decrypted_data(
                    secret=self.project.secret_key, salt=self.project.get_salt()
                )
            else:
                donated_data = None

            context = {**self.participant.get_context_data()}
            if donated_data is not None:
                context.update({'donated_data': donated_data})

            q_config.append(
                QuestionConfigSerializer(question, context=context).data
            )

        return json.dumps(q_config) if return_as_string else q_config

    def get_donation(self, blueprint: DonationBlueprint) -> DataDonation:
        try:
            data_donation = DataDonation.objects.get(
                blueprint=blueprint,
                participant=self.participant
            )

        except DataDonation.DoesNotExist:
            msg = ('Questionnaire Rendering Exception: No donation '
                   f'found for participant {self.participant.pk} and '
                   f'blueprint {blueprint.pk}.')
            ExceptionLogEntry.objects.create(
                project=self.project,
                raised_by=ExceptionRaisers.SERVER,
                message=msg
            )
            raise

        return data_donation

    def create_filter_config(self, return_as_string: bool = True) -> dict:
        """
        Returns a dictionary containing the filter condition configurations
        for the given project that can be passed to the frontend questionnaire
        application.

        Args:
            return_as_string: Whether to return the config stringified with json.dumps()
                or as dict.

        Returns:
            dict: A dictionary containing the project's filter condition
                (key: question/item identifier ['question-<question.pk>'/'item-<item.pk>'];
                value: a list of filter conditions for the question/item).
        """

        f_config = {}
        for question in self.questions:
            question_key = get_filter_config_id(question)
            f_config[question_key] = self.get_filter_config(question)

            items = question.questionitem_set.all()
            for item in items:
                item_key = get_filter_config_id(item)
                f_config[item_key] = self.get_filter_config(item)

        return json.dumps(f_config) if return_as_string else f_config

    def get_filter_config(
            self,
            obj: Union[QuestionBase, QuestionItem]
    ) -> list[dict]:

        filter_conditions = obj.filtercondition_set.filter(
            source_exists=True
        ).order_by('index')
        active_filters = self.remove_inactive_filters(filter_conditions)
        filter_configs = []
        for i, condition in enumerate(active_filters):
            filter_config = FilterConditionSerializer(condition).data

            # Reset combinator value to None for item with the lowest index.
            if i == 0:
                filter_config['combinator'] = None
            filter_configs.append(filter_config)

        return filter_configs

    @staticmethod
    def remove_inactive_filters(
            filter_conditions: QuerySet[FilterCondition]
    ) -> list[FilterCondition]:

        return [fc for fc in filter_conditions if fc.check_source_exists()]
