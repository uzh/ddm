# Dynamic Content

Some texts in DDM can change depending on the participant: for example, show the
participant's ID, thank only participants who donated data, or refer to the donated data in
a question. You do this with *template code* in the text.

Template code works in these texts:

- The briefing text.
- The donation instructions.
- The debriefing text and the [redirect address](../general_project_settings.md#redirect-configuration).
- Question and item texts. In questions linked to a
  [Blueprint](../data_collection_configuration/datadonation/datadonation_overview.md), you
  can also include the participant's donated data (see
  [Data Integration](../data_collection_configuration/questionnaire/questionnaire_data_integration.md)).

Template code has three parts:

- **Variables** insert a value: `{{ participant_id }}`.
- **Tags** add logic, such as conditions: `{% if … %} … {% endif %}`.
- **Filters** change a value: `{{ participant_id|truncatechars:5 }}`.

!!! warning "Always test your template code"

    A mistake in template code, such as a missing `{% endif %}` or an unsupported tag, can
    stop the page from loading for participants. After every change, check the page with
    the [test link](../test_and_launch.md).

## Available Tags and Filters

DDM supports only the variables, tags, and filters listed below. They work like in Django's
template language, which the links describe in more detail.

### Available Variables

Write variables in double curly braces. For example, the text

```django
Your participation ID is {{ participant_id }}.
```

is shown to participants as "Your participation ID is xHQVbrYUYXn5lklW3RGSeouX."

**`participant_id`**

The participant's ID.

**`url_parameter`**

The values of the [extracted URL parameters](../general_project_settings.md#url-parameter-extraction).
Add the parameter's name after a dot. For example, if the link contained
`?channel=email`, `{{ url_parameter.channel }}` shows `email`.

**`briefing_consent`**

Only if you [ask for consent on the briefing page](../data_collection_configuration/briefing.md#configuration-options):
`"1"` if the participant consented and `"0"` if not. These are texts, so compare them
with quotes: `{% if briefing_consent == "1" %}`.

**`donation_info`**

Counts that describe the participant's donations. Add the count's name after a dot, for
example `{{ donation_info.n_consent }}`:

| Name                  | Number of Blueprints…                                                                                |
|-----------------------|------------------------------------------------------------------------------------------------------|
| `n_success`           | from which data was extracted successfully, whether or not the participant consented.                |
| `n_pending`           | for which no extraction was attempted yet, for example because the participant didn't upload a file. |
| `n_failed`            | for which an upload was attempted but failed.                                                        |
| `n_consent`           | from which data was extracted and the participant consented to donate it.                            |
| `n_no_consent`        | from which data was extracted but the participant declined to donate it.                             |
| `n_no_data_extracted` | for which the Extraction Rules removed all entries.                                                  |

**`donated_data`**

Only in questions linked to a Blueprint: the data that this Blueprint extracted for the
participant. For how it's structured and how to use it, see
[Data Integration](../data_collection_configuration/questionnaire/questionnaire_data_integration.md).

### Tags

Write tags in `{% … %}`. Most tags need a closing tag, such as `{% endif %}`. If it's
missing, the text isn't shown at all.

For example, on the debriefing page:

```django
{% if donation_info.n_consent == 0 %}
Unfortunately, you didn't donate any data.
{% else %}
Thank you very much for donating your data!
{% endif %}
```

Participants who donated at least some data see "Thank you very much for donating your
data!".

| Tag                                                                                                                                | What it does                                                           |
|------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| [`{% if %}` … `{% elif %}` … `{% else %}` … `{% endif %}`](https://docs.djangoproject.com/en/5.2/ref/templates/builtins/#if)       | Shows text only if a condition is true.                                |
| [`{% for %}` … `{% endfor %}`](https://docs.djangoproject.com/en/5.2/ref/templates/builtins/#for)                                  | Repeats text for each entry of a list.                                 |
| [`{% ifchanged %}` … `{% else %}` … `{% endifchanged %}`](https://docs.djangoproject.com/en/5.2/ref/templates/builtins/#ifchanged) | In a loop, shows text only if a value differs from the previous entry. |
| [`{% regroup %}`](https://docs.djangoproject.com/en/5.2/ref/templates/builtins/#regroup)                                           | Groups the entries of a list by a field.                               |

### Filters

Add filters to a variable with `|`. For example, `{{ "abcde"|truncatechars:3 }}` shows
"ab…".

| Filter                                                                                               | What it does                                                                                  |
|------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| [`date`](https://docs.djangoproject.com/en/5.2/ref/templates/builtins/#date)                         | Formats a date, for example `{{ entry.time                                                    |date:"d.m.Y" }}`. |
| [`default`](https://docs.djangoproject.com/en/5.2/ref/templates/builtins/#default)                   | Shows a fallback text if the value is empty or missing, for example `{{ url_parameter.channel |default:"unknown" }}`. |
| [`dictsort`](https://docs.djangoproject.com/en/5.2/ref/templates/builtins/#dictsort)                 | Sorts a list by a field, for example `donated_data                                            |dictsort:"time"`. |
| [`dictsortreversed`](https://docs.djangoproject.com/en/5.2/ref/templates/builtins/#dictsortreversed) | Sorts a list by a field in reverse order.                                                     |
| [`first`](https://docs.djangoproject.com/en/5.2/ref/templates/builtins/#first)                       | The first entry of a list.                                                                    |
| [`last`](https://docs.djangoproject.com/en/5.2/ref/templates/builtins/#last)                         | The last entry of a list.                                                                     |
| [`length`](https://docs.djangoproject.com/en/5.2/ref/templates/builtins/#length)                     | The number of entries in a list, or of characters in a text.                                  |
| [`random`](https://docs.djangoproject.com/en/5.2/ref/templates/builtins/#random)                     | A random entry of a list.                                                                     |
| [`truncatechars`](https://docs.djangoproject.com/en/5.2/ref/templates/builtins/#truncatechars)       | Shortens a text to a number of characters, including the "…".                                 |
| [`truncatewords`](https://docs.djangoproject.com/en/5.2/ref/templates/builtins/#truncatewords)       | Shortens a text to a number of words.                                                         |

## Use Cases

### Different Debriefing Texts Depending on Consent

To thank participants differently depending on whether they consented on the briefing page,
use this debriefing text:

```django
{% if briefing_consent == "1" %}
Thank you for taking part in this study.
{% else %}
You decided not to take part in this study. We respect your decision.
{% endif %}

Your participation ID is "{{ participant_id }}". To have your data deleted later, send this
ID to someone@example.org.
```

Participants who consented see:

> Thank you for taking part in this study.
>
> Your participation ID is "xHQVbrYUYXn5lklW3RGSeouX". To have your data deleted later, send
> this ID to someone@example.org.

### Refer to the Donated Data in a Question

See [Data Integration](../data_collection_configuration/questionnaire/questionnaire_data_integration.md).
