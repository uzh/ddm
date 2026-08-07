import copy

from django.db import transaction

from ddm.datadonation.models import DonationBlueprint


def blueprint_name_unique(name: str) -> bool:
    return not DonationBlueprint.objects.filter(name=name).exists()


@transaction.atomic
def copy_blueprint(blueprint: DonationBlueprint) -> DonationBlueprint:
    new_bp = copy.deepcopy(blueprint)
    new_bp.pk = None

    base_name = f"{blueprint.name}_copy"
    new_name = base_name
    i = 0
    while not blueprint_name_unique(new_name):
        i += 1
        new_name = f"{base_name}_{i}"
    new_bp.name = new_name
    new_bp.save(force_insert=True)

    # copy file paths
    for fp in blueprint.blueprintfilepath_set.all():
        fp_new = copy.copy(fp)
        fp_new.pk = None
        fp_new.blueprint = new_bp
        fp_new.save(force_insert=True)

    # copy extraction field & extraction rules
    for field in blueprint.extractionfield_set.all():
        field_new = copy.copy(field)
        field_new.pk = None
        field_new.blueprint = new_bp
        field_new.save(force_insert=True)

        for rule in field.processingrule_set.all():
            rule_new = copy.copy(rule)
            rule_new.pk = None
            rule_new.field = field_new
            rule_new.blueprint = new_bp
            rule_new.save(force_insert=True)

    return new_bp
