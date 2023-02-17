# Generated by Django 3.2.13 on 2022-12-16 13:28

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('ddm', '0019_auto_20221212_2121'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='questionbase',
            options={'base_manager_name': 'non_polymorphic', 'ordering': ['index']},
        ),
        migrations.AlterModelManagers(
            name='matrixquestion',
            managers=[
                ('non_polymorphic', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='multichoicequestion',
            managers=[
                ('non_polymorphic', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='openquestion',
            managers=[
                ('non_polymorphic', django.db.models.manager.Manager()),
                ('objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='questionbase',
            managers=[
                ('non_polymorphic', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='semanticdifferential',
            managers=[
                ('non_polymorphic', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='singlechoicequestion',
            managers=[
                ('non_polymorphic', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='transition',
            managers=[
                ('non_polymorphic', django.db.models.manager.Manager()),
                ('objects', django.db.models.manager.Manager()),
            ],
        ),
    ]