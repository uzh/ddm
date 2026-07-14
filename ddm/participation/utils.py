from __future__ import annotations

import typing

from ddm.questionnaire.constants import FilterSourceTypes

if typing.TYPE_CHECKING:
    from ddm.questionnaire.models import FilterCondition, QuestionBase, QuestionItem


def get_filter_source_config_id(filter_condition: FilterCondition) -> str:
    """Get the ID of the filter's source as used in config dictionaries."""

    if filter_condition.source_type == FilterSourceTypes.QUESTION:
        return get_filter_config_id(filter_condition.source_question)
    if filter_condition.source_type == FilterSourceTypes.QUESTION_ITEM:
        return get_filter_config_id(filter_condition.source_item)
    return filter_condition.source_identifier


def get_filter_target_config_id(filter_condition: FilterCondition) -> str:
    """Get the ID of the filter's target as used in config dictionaries."""

    if filter_condition.target_question:
        return get_filter_config_id(filter_condition.target_question)
    if filter_condition.target_item:
        return get_filter_config_id(filter_condition.target_item)
    msg = "Misconfigured filter condition type"
    raise ValueError(msg)


def get_filter_config_id(obj: QuestionBase | QuestionItem) -> str:
    """
    Returns the passed objects ID used for the filter configuration.

    Args:
        obj (QuestionBase | QuestionItem): Either a QuestionBase or a
            QuestionItem instance.

    Returns:
        str: 'question-<question.pk> for a QuestionBase or
            'item-<item.pk>' for a QuestionItem.
    """

    if not hasattr(obj, "question_type"):
        return f"{FilterSourceTypes.QUESTION_ITEM}-{obj.pk}"
    return f"{FilterSourceTypes.QUESTION}-{obj.pk}"
