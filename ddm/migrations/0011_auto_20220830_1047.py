# Generated by Django 3.2.13 on 2022-08-30 08:47

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ddm', '0010_auto_20220629_1651'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donationblueprint',
            name='exp_file_format',
            field=models.CharField(choices=[('json', 'Json Format')], default='json', max_length=10, verbose_name='Expected file format'),
        ),
        migrations.AlterField(
            model_name='donationblueprint',
            name='expected_fields',
            field=models.TextField(help_text='Put the field names in double quotes (") and separate them with commas ("Field A", "Field B").', validators=[django.core.validators.RegexValidator('^((["][^"]+["]))(\\s*,\\s*((["][^"]+["])))*[,\\s]*$', message='Field must contain one or multiple comma separated strings. Strings must be enclosed in double quotes ("string").')]),
        ),
        migrations.AlterField(
            model_name='donationblueprint',
            name='extracted_fields',
            field=models.TextField(blank=True, help_text='Put the field names in double quotes (") and separate them with commas ("Field A", "Field B").', null=True, validators=[django.core.validators.RegexValidator('^((["][^"]+["]))(\\s*,\\s*((["][^"]+["])))*[,\\s]*$', message='Field must contain one or multiple comma separated strings. Strings must be enclosed in double quotes ("string").')]),
        ),
        migrations.AlterField(
            model_name='donationblueprint',
            name='zip_blueprint',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ddm.zippedblueprint', verbose_name='Zip container'),
        ),
        migrations.AlterField(
            model_name='donationinstruction',
            name='index',
            field=models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.CreateModel(
            name='ExceptionLogEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('exception_type', models.IntegerField()),
                ('message', models.TextField()),
                ('participant', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ddm.participant')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ddm.donationproject')),
            ],
        ),
    ]