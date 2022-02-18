# Generated by Django 3.2.9 on 2022-02-18 14:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('ddm', '0012_auto_20220218_1533'),
    ]

    operations = [
        migrations.CreateModel(
            name='OpenQuestion',
            fields=[
                ('questionbase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='ddm.questionbase')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('ddm.questionbase',),
        ),
        migrations.RenameModel(
            old_name='MultiChoiceQuestionAlt',
            new_name='MultiChoiceQuestion',
        ),
        migrations.RenameModel(
            old_name='QItem',
            new_name='QuestionItem',
        ),
        migrations.RenameModel(
            old_name='QScalePoint',
            new_name='ScalePoint',
        ),
        migrations.RenameModel(
            old_name='SingleChoiceQuestionAlt',
            new_name='SingleChoiceQuestion',
        ),
        migrations.DeleteModel(
            name='TriggerTask',
        ),
    ]