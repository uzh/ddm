from __future__ import annotations

from django.db import models


class FilterSourceTypes(models.TextChoices):
    QUESTION = 'question', 'Question'
    QUESTION_ITEM = 'item', 'Question Item'
    URL_PARAMETER = 'url_parameter', 'URL Parameter'
    SYSTEM = 'system', 'System Variable'
    PARTICIPANT = 'participant', 'Participant Variable'
    DONATION = 'donation', 'Donation Information'


class QuestionType(models.TextChoices):
    GENERIC = 'generic', 'Generic Question'
    SINGLE_CHOICE = 'single_choice', 'Single Choice Question'
    MULTI_CHOICE = 'multi_choice', 'Multi Choice Question'
    MATRIX = 'matrix', 'Matrix Question'
    SEMANTIC_DIFF = 'semantic_diff', 'Semantic Differential'
    OPEN = 'open', 'Open Question'
    TRANSITION = 'transition', 'Text Block'
