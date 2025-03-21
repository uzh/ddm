# Generated by Django 3.2.13 on 2024-10-25 15:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ddm_datadonation', '0002_alter_datadonation_participant'),
        ('ddm_questionnaire', '0004_alter_questionnaireresponse_participant'),
        ('ddm_logging', '0003_alter_exceptionlogentry_participant'),
        ('ddm', '0054_remove_participant_project'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(
                    name='Participant',
                ),
            ],
            database_operations=[
                migrations.AlterModelTable(
                    name='Participant',
                    table='ddm_participation_participant'
                ),
            ]
        )
    ]
