import random
import string

from django.db import migrations, models

def generate_unique_url_id(existing_ids):
    """Generate a unique external_id."""
    while True:
        url_id = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(8))
        if url_id not in existing_ids:  # Ensure uniqueness
            return url_id

def populate_url_id_of_existing_projects(apps, schema_editor):
    DonationProject = apps.get_model('ddm_projects', 'donationproject')
    existing_ids = set(DonationProject.objects.values_list('url_id', flat=True))

    objects_to_update = []
    for project in DonationProject.objects.all():
        if project.url_id is None:
            project.url_id = generate_unique_url_id(existing_ids)
            existing_ids.add(project.url_id)
            objects_to_update.append(project)

    DonationProject.objects.bulk_update(objects_to_update, ['url_id'])


class Migration(migrations.Migration):

    dependencies = [
        ('ddm_projects', '0003_donationproject_active_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='donationproject',
            name='url_id',
            field=models.CharField(max_length=8, unique=True, null=True),
            preserve_default=False,
        ),
        migrations.RunPython(populate_url_id_of_existing_projects),
        migrations.AlterField(
            model_name='donationproject',
            name='url_id',
            field=models.CharField(max_length=8, unique=True, null=False),
        ),
    ]
