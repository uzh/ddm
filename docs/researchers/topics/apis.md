# APIs

With the API, you can download data with a script instead of clicking through the Project
Hub. For example, you can:

- Download all donations, directly into R or Python.
- Update your analysis or a monitoring dashboard automatically while the study is running.
- Show participants a personal report based on their donated data, for example as an
  incentive.

The API has four endpoints:

| Endpoint                                  | What it returns or does                             |
|-------------------------------------------|-----------------------------------------------------|
| [Project Overview](#project-overview)     | The participants, Blueprints, and project settings. |
| [Donations](#donations)                   | The donated data.                                   |
| [Responses](#responses)                   | The questionnaire responses.                        |
| [Delete Participant](#delete-participant) | Deletes a participant and their data.               |

## Before You Start

**1. Create an API token.** In the **Data Center** section of the
[Project Hub](../project_hub.md), click **Manage Remote Access** and create a token. Tokens
are valid for at most 90 days; after that, create a new one.

**2. Find your project ID.** The project ID is shown in the **Overview** section of the
Project Hub, for example `KPHn7aw7`. It's not the same as the **URL Identifier** in the
[General Project Settings](../general_project_settings.md#public-information).

**3. Build the URL.** All endpoints start with your DDM server's address, the path DDM is
installed under (usually `/ddm`), and `/api/project/<project-id>`. For example:

```text
https://ddm.example.org/ddm/api/project/KPHn7aw7/overview
```

**4. Authenticate.** Send the token in the `Authorization` header of every request, as
`Token <your-token>`.

!!! warning "Keep your token and project password secret"

    Anyone with the token can download all data of the project. Don't write the token or the
    project password into scripts that you share or put under version control. Store them
    in environment variables instead, as in the [examples](#examples) below.

### Projects with Enhanced Encryption

For projects with
[enhanced encryption](../create_project.md#advanced-options-enhanced-encryption), the
Donations and Responses endpoints also need the project password, in the `X-Project-Secret`
header. Without the correct password, they return the status `422`. The Project Overview and
Delete Participant endpoints don't need it.

In the API, projects with enhanced encryption are called *super secret* projects.

### Rate Limit

Each token can make up to 100 requests per minute. Above that, the API returns the status
`429`. Your DDM administrator can change this limit.

## Examples

These examples download all donations of a project. They first get the participant IDs from
the Project Overview endpoint and then download the donations of those participants.

=== "Python"

    ```python
    import os
    import requests

    BASE_URL = "https://ddm.example.org/ddm/api/project/KPHn7aw7"
    HEADERS = {"Authorization": f"Token {os.environ['DDM_TOKEN']}"}
    # For projects with enhanced encryption, also send the project password:
    # HEADERS["X-Project-Secret"] = os.environ["DDM_PROJECT_PASSWORD"]

    overview = requests.get(f"{BASE_URL}/overview", headers=HEADERS)
    overview.raise_for_status()
    participant_ids = [p["external_id"] for p in overview.json()["participants"]]

    donations = requests.get(
        f"{BASE_URL}/donations",
        headers=HEADERS,
        params={"participants": ",".join(participant_ids)},
    )
    donations.raise_for_status()
    data = donations.json()
    ```

=== "R"

    ```r
    library(httr2)

    base_url <- "https://ddm.example.org/ddm/api/project/KPHn7aw7"
    token <- Sys.getenv("DDM_TOKEN")

    ddm_request <- function(path) {
      request(paste0(base_url, path)) |>
        req_headers(Authorization = paste("Token", token))
      # For projects with enhanced encryption, also add:
      # |> req_headers(`X-Project-Secret` = Sys.getenv("DDM_PROJECT_PASSWORD"))
    }

    overview <- ddm_request("/overview") |> req_perform() |> resp_body_json()
    participant_ids <- vapply(overview$participants, \(p) p$external_id, character(1))

    data <- ddm_request("/donations") |>
      req_url_query(participants = paste(participant_ids, collapse = ",")) |>
      req_perform() |>
      resp_body_json()
    ```

!!! note "Many participants"

    With many participants, the URL can get too long. Request the donations in batches of,
    for example, 20 participants.

## Endpoints

All endpoints can return these errors:

| Status | Message                | Meaning                                                    |
|--------|------------------------|------------------------------------------------------------|
| `401`  | Authentication failed. | The token is missing, invalid, or expired.                 |
| `403`  | Permission Denied.     | The token is valid but not permitted to make this request. |
| `404`  | Project not found.     | No project exists with this project ID.                    |
| `429`  |                        | Too many requests (see [Rate Limit](#rate-limit)).         |

The Donations and Responses endpoints can also return:

| Status | Message                      | Meaning                                                                                      |
|--------|------------------------------|----------------------------------------------------------------------------------------------|
| `422`  | Missing or incorrect secret. | The project uses enhanced encryption, and the `X-Project-Secret` header is missing or wrong. |

### Project Overview

Returns the participants, the Blueprints, and the project settings.

`GET /api/project/<project-id>/overview`

| Header          | Required | Description          |
|-----------------|----------|----------------------|
| `Authorization` | Yes      | `Token <your-token>` |

**Response:**

```json
{
    "participants": [
        {
            "external_id": "<string: participant ID>",
            "start_time": "<string: date and time (ISO 8601)>",
            "end_time": "<string: date and time (ISO 8601), or null>",
            "completed": "<boolean>",
            "url_parameter": "<object: extracted URL parameters>",
            "extra_data": "<object: additional data, for example briefing consent>",
            "current_step": "<integer: 0 = started, 1 = briefing completed, 2 = data donation completed, 3 = questionnaire completed>"
        }
    ],
    "blueprints": [
        {
            "id": "<integer: Blueprint ID>",
            "name": "<string>",
            "description": "<string or null>",
            "format": "<string: json, csv, or txt>",
            "expected_fields": "<list of strings>",
            "exp_fields_regex_matching": "<boolean>",
            "nested_expected_fields": "<list of strings>",
            "nested_exp_fields_regex_matching": "<boolean>",
            "parser_config": "<object: format-specific settings, see below>",
            "nested_display_by_root_item": "<boolean: Group entries by parent item>",
            "nested_entry_exclusion_allowed": "<boolean: Allow item exclusion>",
            "fields_to_extract": "<list of strings: fields with Keep in donation>",
            "extraction_fields": "<list: Relevant Fields, see below>",
            "file_paths": "<list of {\"path\": string, \"is_regex\": boolean}>",
            "extraction_rules": "<list: Extraction Rules, see below>",
            "is_backup": "<boolean>",
            "backup_ids": "<list of integers: IDs of this Blueprint's backups>"
        }
    ],
    "project": {
        "url_id": "<string: project ID>",
        "name": "<string>",
        "date_created": "<string: date and time (ISO 8601)>",
        "contact_information": "<string>",
        "data_protection_statement": "<string>",
        "slug": "<string: URL Identifier>",
        "url_parameter_enabled": "<boolean>",
        "expected_url_parameters": "<string>",
        "active": "<boolean>"
    },
    "metadata": {
        "n_blueprints": "<integer>",
        "n_participants": "<integer>"
    }
}
```

`parser_config` contains the format-specific
[Blueprint settings](../data_collection_configuration/datadonation/datadonation_configuration.md#blueprint-configuration):

- `json`: `extraction_root`, `nested_loop_path`, `array_join_separator`, and
  `max_root_entries` (reserved for a future feature; always `null`).
- `csv`: `delimiter`.
- `txt`: `record_separator`, `field_separator`, `kv_separator`, `skip_header_lines`,
  `skip_footer_lines`, `ignore_blank_lines`, and `trim_whitespace`.

Each entry in `extraction_fields` is a
[Relevant Field](../data_collection_configuration/datadonation/datadonation_configuration.md#relevant-fields)
with `id`, `scope` (`root` or `nested`), `expected_name`, `match_regex`, `keep_in_donation`,
and `alias` (the **Rename to** value).

Each entry in `extraction_rules` is an
[Extraction Rule](../data_collection_configuration/datadonation/datadonation_configuration.md#extraction-rules)
with `id`, `field`, `comparison_operator`, `comparison_value`, and `replacement_value`.

**Example request:**

```http
GET /ddm/api/project/KPHn7aw7/overview HTTP/1.1
Host: ddm.example.org
Authorization: Token 1176fcf7d0203db1e097861ef7442b328f1bb7f1
```

### Donations

Returns the donated data.

`GET /api/project/<project-id>/donations`

| Parameter                  | Required | Description                                                                                            |
|----------------------------|----------|--------------------------------------------------------------------------------------------------------|
| `participants`             | Yes      | Comma-separated participant IDs, for example `riZVabtDI5jCpO6tvQQOTG6A,wm2tpQIFFIWaqYbgizwTif8S`.      |
| `blueprints`               | No       | Comma-separated Blueprint IDs. If omitted, all Blueprints are returned.                                |
| `include_broken_test_runs` | No       | `true` to include [test runs](../test_and_launch.md) in which steps were skipped. Excluded by default. |

| Header             | Required                              | Description           |
|--------------------|---------------------------------------|-----------------------|
| `Authorization`    | Yes                                   | `Token <your-token>`  |
| `X-Project-Secret` | For projects with enhanced encryption | The project password. |

**Response:** The donations, grouped by Blueprint ID:

```json
{
    "blueprints": {
        "<Blueprint ID>": {
            "blueprint_name": "<string>",
            "donations": [
                {
                    "participant": "<string: participant ID>",
                    "data": "<list: the extracted entries>",
                    "time_submitted": "<string: date and time (ISO 8601)>",
                    "data_extraction_state": "<string: DATA_EXTRACTED, NOT_ATTEMPTED, FAILED, or NO_DATA_EXTRACTED>",
                    "consent": "<boolean>",
                    "n_data_entries": "<integer or null>"
                }
            ]
        }
    },
    "metadata": {
        "n_blueprints": "<integer>"
    }
}
```

For the meaning of `data_extraction_state`, see
[Download → Participation Overview](../data_center/data_download.md#participation-overview).

**Example:** Donations of two participants for Blueprint `1`:

```http
GET /ddm/api/project/KPHn7aw7/donations?participants=riZVabtDI5jCpO6tvQQOTG6A,wm2tpQIFFIWaqYbgizwTif8S&blueprints=1 HTTP/1.1
Host: ddm.example.org
Authorization: Token 1176fcf7d0203db1e097861ef7442b328f1bb7f1
```

```json
{
    "blueprints": {
        "1": {
            "blueprint_name": "Watch History",
            "donations": [
                {
                    "participant": "riZVabtDI5jCpO6tvQQOTG6A",
                    "data": [
                        {"title": "How to Bake Sourdough Bread", "time": "2025-01-14T18:02:11"},
                        {"title": "10 Minute Morning Yoga", "time": "2025-01-13T07:45:30"}
                    ],
                    "time_submitted": "2025-01-15T09:16:36.453322+01:00",
                    "data_extraction_state": "DATA_EXTRACTED",
                    "consent": true,
                    "n_data_entries": 2
                },
                {
                    "participant": "wm2tpQIFFIWaqYbgizwTif8S",
                    "data": [
                        {"title": "Learn Python in 1 Hour", "time": "2025-01-12T20:15:00"}
                    ],
                    "time_submitted": "2025-01-15T09:16:36.456329+01:00",
                    "data_extraction_state": "DATA_EXTRACTED",
                    "consent": true,
                    "n_data_entries": 1
                }
            ]
        }
    },
    "metadata": {
        "n_blueprints": 1
    }
}
```

### Responses

Returns the questionnaire responses.

`GET /api/project/<project-id>/responses`

| Parameter                  | Required | Description                                                                                                           |
|----------------------------|----------|-----------------------------------------------------------------------------------------------------------------------|
| `participants`             | No       | Comma-separated participant IDs. If omitted, the responses of all participants are returned.                          |
| `include_snapshot`         | No       | `true` to include the questionnaire as each participant saw it (`questionnaire_snapshot` and `questionnaire_config`). |
| `include_broken_test_runs` | No       | `true` to include [test runs](../test_and_launch.md) in which steps were skipped. Excluded by default.                |
| `csv`                      | No       | `true` to get a CSV file instead of JSON.                                                                             |

| Header             | Required                              | Description           |
|--------------------|---------------------------------------|-----------------------|
| `Authorization`    | Yes                                   | `Token <your-token>`  |
| `X-Project-Secret` | For projects with enhanced encryption | The project password. |

**Response:**

```json
{
    "responses": [
        {
            "participant": "<string: participant ID>",
            "response_data": "<object: variable name and answer pairs>",
            "time_submitted": "<string: date and time (ISO 8601)>",
            "questionnaire_complete": "<boolean: true if the participant submitted the last page>",
            "questionnaire_snapshot": "<object: only with include_snapshot=true>",
            "questionnaire_config": "<list: only with include_snapshot=true>"
        }
    ],
    "metadata": {
        "n_responses": "<integer>"
    }
}
```

For the answer codes `-77` and `-99`, see
[Download → Download Questionnaire Responses](../data_center/data_download.md#download-questionnaire-responses).

**Example:**

```http
GET /ddm/api/project/KPHn7aw7/responses?participants=cSCslglsu2Mv0j0ryz8lGrcA HTTP/1.1
Host: ddm.example.org
Authorization: Token 1176fcf7d0203db1e097861ef7442b328f1bb7f1
```

```json
{
    "responses": [
        {
            "participant": "cSCslglsu2Mv0j0ryz8lGrcA",
            "response_data": {"media_use": "3", "media_use_reason": "-99"},
            "time_submitted": "2025-01-14T13:19:21.998413+01:00",
            "questionnaire_complete": true
        }
    ],
    "metadata": {"n_responses": 1}
}
```

### Delete Participant

Deletes a participant, including their donations and responses. This can't be undone.

`DELETE /api/project/<project-id>/participant/<participant-id>/delete`

| Header          | Required | Description          |
|-----------------|----------|----------------------|
| `Authorization` | Yes      | `Token <your-token>` |

If the participant doesn't exist, the endpoint returns `404`.

**Example:**

```http
DELETE /ddm/api/project/KPHn7aw7/participant/I8RohmYJrcaCLxHP1bnEuuHn/delete HTTP/1.1
Host: ddm.example.org
Authorization: Token 1176fcf7d0203db1e097861ef7442b328f1bb7f1
```

```json
{
    "message": "Participant with external id 'I8RohmYJrcaCLxHP1bnEuuHn' successfully deleted."
}
```
