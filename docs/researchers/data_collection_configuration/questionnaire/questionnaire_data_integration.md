# Data Integration

Questions linked to a [Blueprint](../datadonation/datadonation_overview.md) can include the
participant's donated data. For example, you can ask about a specific video from the
participant's watch history:

> Why did you watch "How to Bake Sourdough Bread"?

DDM fills in the data for each participant when the question is shown.

!!! note

    This isn't available for projects with
    [enhanced encryption](../../create_project.md#advanced-options-enhanced-encryption).

## How the Donated Data Is Structured

In a question linked to a Blueprint, the variable `donated_data` contains the data that this
Blueprint extracted for the participant. It's a list of entries, one per row. Each entry
contains the [Relevant Fields](../datadonation/datadonation_configuration.md#relevant-fields)
of the Blueprint, under their **Rename to** names if you set them.

For example, a watch-history Blueprint with the fields `title` and `time` could produce:

| title                       | time             |
|-----------------------------|------------------|
| How to Bake Sourdough Bread | 2026-04-02 15:30 |
| Why are Harry's eyes blue   | 2026-04-01 14:09 |

The entries keep the order of the platform's file. Check whether the first entry is the
oldest or the newest before you refer to "the last video".

## Include Data in a Question

Write variables in double curly braces. Use the entry's position (starting at `0`) and the
field name, separated by dots:

```django
Why did you watch "{{ donated_data.0.title }}"?
```

To list several entries, use a loop. This example lists the first three titles:

```django
Which of these videos do you remember?
{% for entry in donated_data %}{% if forloop.counter <= 3 %}
- {{ entry.title }}
{% endif %}{% endfor %}
```

You can also use the variables available in all texts, such as `{{ participant_id }}` and
`{{ url_parameter.<name> }}`. For all variables and more examples, see
[Template Rendering](../../topics/templating_features.md).

To show or hide questions depending on the donation, use
[filters](questionnaire_configuration.md#filter-configuration).
