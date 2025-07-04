# Generated by Django 4.2.16 on 2025-03-12 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ddm_questionnaire', '0009_rename_add_border_scalepoint_secondary_point'),
    ]

    operations = [
        migrations.RenameField(
            model_name='scalepoint',
            old_name='label',
            new_name='input_label',
        ),
        migrations.AddField(
            model_name='matrixquestion',
            name='show_scale_headings',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='scalepoint',
            name='heading_label',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
