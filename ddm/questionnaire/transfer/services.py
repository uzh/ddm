from __future__ import annotations

import copy
from typing import TYPE_CHECKING

from django.db import transaction
from django.utils import timezone

from ddm import VERSION as DDM_VERSION
from ddm.core.utils.transfer.id_mapping import AllocationIDs, IdMap, LocalIdAllocator
from ddm.core.utils.transfer.schema import EXPORT_KIND_QUESTIONNAIRE, SCHEMA_VERSION
from ddm.datadonation.models import DonationBlueprint
from ddm.questionnaire.constants import FilterSourceTypes, QuestionType
from ddm.questionnaire.models import (
    FilterCondition,
    MatrixQuestion,
    MultiChoiceQuestion,
    OpenQuestion,
    QuestionBase,
    QuestionItem,
    ScalePoint,
    SemanticDifferential,
    SingleChoiceQuestion,
    Transition,
)

if TYPE_CHECKING:
    from ddm.projects.models import DonationProject

QUESTION_CLASSES: dict[str, type[QuestionBase]] = {
    QuestionType.GENERIC: QuestionBase,
    QuestionType.SINGLE_CHOICE: SingleChoiceQuestion,
    QuestionType.MULTI_CHOICE: MultiChoiceQuestion,
    QuestionType.OPEN: OpenQuestion,
    QuestionType.MATRIX: MatrixQuestion,
    QuestionType.SEMANTIC_DIFF: SemanticDifferential,
    QuestionType.TRANSITION: Transition,
}


def reset_pk(instance) -> None:  # noqa: ANN001
    """
    Clear pk for `instance`, including inherited parent-link pks for
    multi-table-inherited (e.g. django-polymorphic) models.

    A plain `instance.pk = None` only clears the local pk field. For MTI
    subclasses, ancestor tables have their own separately-stored pk
    attribute (e.g. `id` inherited from a polymorphic base model) that
    must also be cleared, or Django will UPDATE the ancestor row instead
    of inserting a new one.
    """
    for parent in instance._meta.get_parent_list():  # noqa: SLF001
        setattr(instance, parent._meta.pk.attname, None)  # noqa: SLF001
    instance.pk = None


def variable_name_unique(name: str, project: DonationProject) -> bool:
    return not QuestionBase.objects.filter(variable_name=name, project=project).exists()


@transaction.atomic
def copy_question(question: QuestionBase) -> QuestionBase:
    new_q = copy.deepcopy(question)
    reset_pk(new_q)

    base_variable_name = f"{question.variable_name}_copy"
    new_variable_name = base_variable_name
    i = 0
    while not variable_name_unique(new_variable_name, question.project):
        i += 1
        new_variable_name = f"{base_variable_name}_{i}"
    new_q.variable_name = new_variable_name
    new_q.name = f"{question.name} (copy)"
    new_q.save(force_insert=True)

    # copy question item
    for item in question.questionitem_set.all():
        item_new = copy.deepcopy(item)
        item_new.pk = None
        item_new.question = new_q
        item_new.save(force_insert=True)

        # copy item filter conditions
        filter_conditions = FilterCondition.objects.filter(target_item=item)
        for fc in filter_conditions:
            new_fc = copy.deepcopy(fc)
            new_fc.pk = None
            new_fc.target_item = item_new
            new_fc.save(force_insert=True)

    # copy scale points
    for sp in question.scalepoint_set.all():
        sp_new = copy.deepcopy(sp)
        sp_new.pk = None
        sp_new.question = new_q
        sp_new.save(force_insert=True)

    # copy question filter conditions
    filter_conditions = FilterCondition.objects.filter(target_question=question)
    for fc in filter_conditions:
        new_fc = copy.deepcopy(fc)
        new_fc.pk = None
        new_fc.target_question = new_q
        new_fc.save(force_insert=True)

    return new_q


def _get_question_type_options(question: QuestionBase) -> dict:
    """Type-specific fields not shared by all QuestionBase subtypes."""
    if question.question_type == QuestionType.OPEN:
        return {
            "display": question.display,
            "input_type": question.input_type,
            "min_input_length": question.min_input_length,
            "max_input_length": question.max_input_length,
            "min_number_value": question.min_number_value,
            "max_number_value": question.max_number_value,
            "multi_item_response": question.multi_item_response,
        }

    if question.question_type == QuestionType.MATRIX:
        return {"show_scale_headings": question.show_scale_headings}

    return {}


def _serialize_filter_condition(
    fc: FilterCondition, allocator: LocalIdAllocator
) -> dict:
    if fc.target_question_id:
        target_local_id = allocator.get_or_create(
            AllocationIDs.QUESTION, fc.target_question_id
        )
    else:
        target_local_id = allocator.get_or_create(
            AllocationIDs.QUESTION_ITEM, fc.target_item_id
        )

    source_local_id = None
    if fc.source_type == FilterSourceTypes.QUESTION and fc.source_question_id:
        source_local_id = allocator.get_or_create(
            AllocationIDs.QUESTION, fc.source_question_id
        )
    elif fc.source_type == FilterSourceTypes.QUESTION_ITEM and fc.source_item_id:
        source_local_id = allocator.get_or_create(
            AllocationIDs.QUESTION_ITEM, fc.source_item_id
        )

    return {
        "index": fc.index,
        "combinator": fc.combinator,
        "condition_operator": fc.condition_operator,
        "condition_value": fc.condition_value,
        "target_local_id": target_local_id,
        "source_type": fc.source_type,
        "source_local_id": source_local_id,
        # Identifier is only meaningful (and only exported) for non-FK source types
        # (url_parameter/system/participant/donation); for FK-based
        # sources it normally holds the source's real pk, which isn't
        # portable, so it's rebuilt from source_local_id at import time.
        "source_identifier": (
            fc.source_identifier
            if fc.source_type
            not in (FilterSourceTypes.QUESTION, FilterSourceTypes.QUESTION_ITEM)
            else None
        ),
    }


def serialize_questions(
    project: DonationProject,
    allocator: LocalIdAllocator,
    *,
    include_blueprint_ref: bool = True,
) -> list[dict]:
    """
    Serialize all of a project's questions (+ nested QuestionItem,
    ScalePoint, FilterCondition) into a list of JSON-safe dicts for export.

    `include_blueprint_ref`: True for whole-project export/copy, where a
    question's `blueprint` link is represented as a local id resolved
    against the accompanying blueprint export. False for a standalone
    questionnaire export, where there is no accompanying blueprint graph -
    the link is instead represented by the blueprint's `name`, resolved by
    lookup in the target project at import time.
    """
    questions = list(
        project.questionbase_set.select_related("blueprint")
        .prefetch_related("questionitem_set", "scalepoint_set")
        .all()
    )

    # Assign local ids for every question/item up front, so filter
    # conditions can always resolve a target/source regardless of
    # iteration order (a filter can reference any question/item in the
    # project, not just ones processed so far).
    for question in questions:
        allocator.get_or_create(AllocationIDs.QUESTION, question.pk)
        for item in question.questionitem_set.all():
            allocator.get_or_create(AllocationIDs.QUESTION_ITEM, item.pk)

    questions_data = []
    for question in questions:
        blueprint_local_id = None
        blueprint_name = None
        if question.blueprint_id:
            if include_blueprint_ref:
                blueprint_local_id = allocator.get_or_create(
                    AllocationIDs.BLUEPRINT, question.blueprint_id
                )
            else:
                blueprint_name = question.blueprint.name

        items = [
            {
                "local_id": allocator.get_or_create(
                    AllocationIDs.QUESTION_ITEM, item.pk
                ),
                "index": item.index,
                "label": item.label,
                "label_alt": item.label_alt,
                "value": item.value,
                "randomize": item.randomize,
            }
            for item in question.questionitem_set.all()
        ]

        scale_points = [
            {
                "index": sp.index,
                "input_label": sp.input_label,
                "heading_label": sp.heading_label,
                "value": sp.value,
                "secondary_point": sp.secondary_point,
            }
            for sp in question.scalepoint_set.all()
        ]

        filter_conditions = [
            _serialize_filter_condition(fc, allocator)
            for fc in question.get_active_filters()
        ]
        for item in question.questionitem_set.all():
            filter_conditions += [
                _serialize_filter_condition(fc, allocator)
                for fc in item.get_active_filters()
            ]

        questions_data.append(
            {
                "local_id": allocator.get_or_create(
                    AllocationIDs.QUESTION, question.pk
                ),
                "blueprint_local_id": blueprint_local_id,
                "blueprint_name": blueprint_name,
                "question_type": question.question_type,
                "name": question.name,
                "page": question.page,
                "index": question.index,
                "variable_name": question.variable_name,
                "text": question.text,
                "requirement_level": question.requirement_level,
                "randomize_items": getattr(question, "randomize_items", False),
                "type_options": _get_question_type_options(question),
                "items": items,
                "scale_points": scale_points,
                "filter_conditions": filter_conditions,
            }
        )

    return questions_data


def _resolve_question_blueprint(
    q_data: dict,
    project: DonationProject,
    blueprint_id_map: IdMap | None,
    warnings: list[str],
) -> DonationBlueprint | None:
    if blueprint_id_map is not None:
        return blueprint_id_map.get(q_data.get("blueprint_local_id"))

    blueprint_name = q_data.get("blueprint_name")
    if not blueprint_name:
        return None

    blueprint = DonationBlueprint.objects.filter(
        project=project, name=blueprint_name
    ).first()
    if blueprint is None:
        label = q_data.get("name") or q_data.get("variable_name") or "?"
        warnings.append(
            f'Question "{label}" referenced blueprint "{blueprint_name}", '
            f"which was not found in the target project; the question was "
            f"imported without a linked blueprint."
        )
    return blueprint


def _build_filter_condition(fc_data: dict, id_map: IdMap) -> None:
    target = id_map.get(fc_data.get("target_local_id"))
    if target is None:
        # Dangling target reference; well-formed payloads never hit this
        # (schema.validate_envelope rejects it up front) - guard kept as a
        # defensive no-op rather than risking an uncaught exception below.
        return

    source_type = fc_data.get("source_type")
    if source_type in (FilterSourceTypes.QUESTION, FilterSourceTypes.QUESTION_ITEM):
        source_obj = id_map.get(fc_data.get("source_local_id"))
        # source_identifier holds the source's pk-as-string for FK-based
        # sources (see FilterCondition.clean()); rebuilt here against the
        # newly created source object rather than carried over as JSON.
        source_identifier = str(source_obj.pk) if source_obj else ""
    else:
        source_identifier = fc_data.get("source_identifier") or ""

    fc = FilterCondition(
        source_type=source_type,
        source_identifier=source_identifier,
        index=fc_data.get("index", 1),
        combinator=fc_data.get("combinator", FilterCondition.ConditionCombinators.AND),
        condition_operator=fc_data.get(
            "condition_operator", FilterCondition.ConditionOperators.EQUALS
        ),
        condition_value=fc_data.get("condition_value"),
        **(
            {"target_item": target}
            if isinstance(target, QuestionItem)
            else {"target_question": target}
        ),
    )
    fc.full_clean(validate_unique=False)
    fc.save(force_insert=True)


@transaction.atomic
def build_questions(
    data: list[dict],
    project: DonationProject,
    *,
    blueprint_id_map: IdMap | None = None,
) -> tuple[list[QuestionBase], list[str]]:
    """
    Create new questions (+ nested QuestionItem, ScalePoint,
    FilterCondition) in `project`, from a list of dicts produced by
    `serialize_questions()`. Returns (created_questions, warnings) - warnings
    are non-fatal issues (e.g. an unresolved blueprint_name lookup) that
    the caller should surface to the user, not raise as errors.

    `blueprint_id_map`: see `_resolve_question_blueprint()`.
    """
    id_map = IdMap()
    warnings: list[str] = []
    created_questions: list[QuestionBase] = []

    # Pass 1: create questions, items, and scale points. Filter conditions
    # are deferred to pass 2, since they may reference any question/item
    # in this import, including ones not yet created.
    for q_data in data:
        blueprint = _resolve_question_blueprint(
            q_data, project, blueprint_id_map, warnings
        )

        base_variable_name = q_data["variable_name"]
        new_variable_name = base_variable_name
        suffix = 0
        while not variable_name_unique(new_variable_name, project):
            suffix += 1
            new_variable_name = f"{base_variable_name}_{suffix}"

        question_class = QUESTION_CLASSES.get(q_data["question_type"], QuestionBase)
        field_kwargs = dict(q_data.get("type_options") or {})
        if hasattr(question_class, "randomize_items"):
            field_kwargs["randomize_items"] = q_data.get("randomize_items", False)

        new_q = question_class(
            project=project,
            blueprint=blueprint,
            question_type=q_data["question_type"],
            name=q_data.get("name", ""),
            page=q_data.get("page", 1),
            index=q_data.get("index", 1),
            variable_name=new_variable_name,
            text=q_data.get("text", ""),
            requirement_level=q_data.get(
                "requirement_level", QuestionBase.RequirementLevel.NOT_REQUIRED
            ),
            **field_kwargs,
        )
        new_q.full_clean(validate_unique=False)
        new_q.save(force_insert=True)
        id_map.register(q_data.get("local_id"), new_q)
        created_questions.append(new_q)

        for item_data in q_data.get("items", []):
            item = QuestionItem.objects.create(
                question=new_q,
                index=item_data.get("index", 1),
                label=item_data.get("label", ""),
                label_alt=item_data.get("label_alt", ""),
                value=item_data.get("value"),
                randomize=item_data.get("randomize", False),
            )
            id_map.register(item_data.get("local_id"), item)

        for sp_data in q_data.get("scale_points", []):
            ScalePoint.objects.create(
                question=new_q,
                index=sp_data.get("index", 1),
                input_label=sp_data.get("input_label", ""),
                heading_label=sp_data.get("heading_label", ""),
                value=sp_data.get("value"),
                secondary_point=sp_data.get("secondary_point", False),
            )

    # Pass 2: filter conditions, now that every question/item created in
    # this import is registered in id_map.
    for q_data in data:
        for fc_data in q_data.get("filter_conditions", []):
            _build_filter_condition(fc_data, id_map)

    return created_questions, warnings


def export_questions(project: DonationProject) -> dict:
    """Wraps `serialize_questions()` in a standalone export envelope."""
    questions = serialize_questions(
        project, LocalIdAllocator(), include_blueprint_ref=False
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "export_kind": EXPORT_KIND_QUESTIONNAIRE,
        "exported_at": timezone.now().isoformat(),
        "ddm_version": DDM_VERSION,
        "questions": questions,
    }
