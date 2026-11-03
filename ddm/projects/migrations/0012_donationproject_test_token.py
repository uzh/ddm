import binascii
import os

from django.db import migrations, models


def generate_test_token() -> str:
    """Mirrors ddm.projects.models.generate_test_token() - inlined so this
    migration doesn't depend on the model module's current contents."""
    return binascii.hexlify(os.urandom(20)).decode()


def populate_test_tokens(apps, schema_editor):
    DonationProject = apps.get_model("ddm_projects", "DonationProject")
    for project in DonationProject.objects.all().iterator():
        DonationProject.objects.filter(pk=project.pk).update(
            test_token=generate_test_token()
        )


class Migration(migrations.Migration):

    dependencies = [
        ('ddm_projects', '0011_donationproject_wrapped_private_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='donationproject',
            name='test_token',
            field=models.CharField(max_length=40, unique=True, null=True),
            preserve_default=False,
        ),
        migrations.RunPython(populate_test_tokens, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='donationproject',
            name='test_token',
            field=models.CharField(editable=False, max_length=40, unique=True),
        ),
    ]
