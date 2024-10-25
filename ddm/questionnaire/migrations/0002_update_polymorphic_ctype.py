from django.db import migrations, connection
from django.contrib.contenttypes.models import ContentType


def update_polymorphic_ctype(apps, schema_editor):
    # Define a mapping from old model paths to new model paths
    content_type_mapping = {
        'ddm.matrixquestion': 'ddm_questionnaire.MatrixQuestion',
        'ddm.multichoicequestion': 'ddm_questionnaire.MultiChoiceQuestion',
        'ddm.openquestion': 'ddm_questionnaire.OpenQuestion',
        'ddm.semanticdifferential': 'ddm_questionnaire.SemanticDifferential',
        'ddm.singlechoicequestion': 'ddm_questionnaire.SingleChoiceQuestion',
        'ddm.transition': 'ddm_questionnaire.Transition',
    }

    cursor = connection.cursor()

    for old_model, new_model in content_type_mapping.items():
        old_app_label, old_model_name = old_model.split('.')
        new_app_label, new_model_name = new_model.split('.')

        # Get the old and new ContentTypes
        try:
            old_ctype = ContentType.objects.get(app_label=old_app_label, model=old_model_name.lower())
            new_ctype = ContentType.objects.get(app_label=new_app_label, model=new_model_name.lower())
        except ContentType.DoesNotExist:
            continue

        # Update the polymorphic_ctype_id directly using raw SQL
        sql = f"""
        UPDATE ddm_questionnaire_questionbase
        SET polymorphic_ctype_id = %s
        WHERE polymorphic_ctype_id = %s
        """
        cursor.execute(sql, [new_ctype.id, old_ctype.id])

class Migration(migrations.Migration):

    dependencies = [
        ('ddm_questionnaire', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name')
    ]

    operations = [
        migrations.RunPython(update_polymorphic_ctype),
    ]
