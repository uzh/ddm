# General Project Settings

The general project settings have four sections:

| Section                                                   | What it's for                                                                                                           |
|-----------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| [**Public Information**](#public-information)             | What participants see about your project, such as its name and your contact details, and whether the project is active. |
| [**URL Parameter Extraction**](#url-parameter-extraction) | Save information that's passed in the participation link, such as a participant ID from your survey tool.               |
| [**Redirect Configuration**](#redirect-configuration)     | Send participants to another website at the end, such as a follow-up survey.                                            |
| [**Branding**](#branding)                                 | Your colors and logos in the Participation Interface.                                                                   |

## Public Information

This information is visible to participants and helps them understand and trust your study.

!!! setting-details "Settings"

    ---

    **Project Name**

    The project name shown in the participant's browser tab.

    ---

    **URL Identifier**

    The part of the participation link that identifies your project. For example, with
    `my-study`, participants take part at `https://your-ddm-server/ddm/my-study/briefing`.

    You can use letters, numbers, hyphens (`-`), and underscores (`_`).

    ---

    **Active**

    Whether participants can take part. While a project is inactive, participants who open
    the link see a page saying that participation isn't possible at the moment.

    ---

    **Contact Information**

    Contact details of the researcher responsible for the project. Participants can open
    them from the footer at every step, so they know who runs the study and how to reach you.

    ---

    **Data Protection Statement**

    How you process the collected data. Participants can open it from the footer at every
    step.

## URL Parameter Extraction

A link can carry extra information after a question mark, called *URL parameters*. For
example, in `https://your-ddm-server/ddm/my-study/briefing?participant=ID123`, the parameter
`participant` has the value `ID123`. DDM can save these values for each participant.

This is useful for:

- **Linking DDM to other tools.** If participants come from a survey tool (for example,
  SoSciSurvey or Qualtrics) or a recruitment partner, pass their ID in the link
  (`?participant=ID123`). You can then match the donated data to their survey responses.
- **Tracking recruitment channels.** Use a different link for each channel (for example,
  `?channel=email` and `?channel=social-media`) to see where participants came from.

!!! setting-details "Settings"

    ---

    **URL parameter extraction enabled**

    Whether DDM saves URL parameters. If enabled, DDM saves them when a participant opens the
    briefing page.

    ---

    **Expected URL parameter**

    The names of the parameters to save. Separate multiple names with semicolons, for
    example `participant;channel`.

    The values are saved for each participant and included in the data download. If a
    parameter is missing from the link, the value is empty (shown as an empty cell or
    `null`, depending on the program you open the file with). DDM ignores all other
    parameters.

## Redirect Configuration

At the end of the study, DDM can show participants a button on the debriefing page that
takes them to another website.

This is useful for:

- **Linking DDM to other tools.** Send participants to a follow-up survey (for example, in
  SoSciSurvey or Qualtrics) or back to a recruitment partner, and pass their ID in the link
  (see below).
- **Linking to your project website.**

!!! setting-details "Settings"

    ---

    **Redirect enabled**

    Whether the debriefing page shows a button that links to the **Redirect address**.

    ---

    **Redirect address**

    The URL the button links to. Required if **Redirect enabled** is on.

    !!! tip "Pass information in the redirect link"

        The URL can include variables that DDM fills in for each participant:

        - `{{ participant_id }}`: The participant's ID.
        - `{{ project_id }}`: The project's ID.
        - `{{ url_parameter.<name> }}`: The value of an
          [extracted URL parameter](#url-parameter-extraction), for example
          `{{ url_parameter.participant }}`.

        For example, to send participants back to your survey with the ID they arrived with:
        `https://survey.example.org?participant={{ url_parameter.participant }}`

        For all available variables, see [Template Rendering](topics/templating_features.md).

## Branding

Customize how the Participation Interface looks: set its colors and add up to two logos.

!!! setting-details "Settings"

    ---

    **Show project title**

    Whether the project title is shown in the header.

    ---

    **Primary Color**

    The color of buttons and highlights. DDM creates lighter and darker shades from it
    automatically. Choose a dark color so that button text stays readable.

    ---

    **Background Color**

    The background color of all pages. Choose a very light color.

    ---

    **Header Image Left** and **Header Image Right**

    Images shown on the left and right side of the header, for example your institution's
    or project's logo. Use a JPEG or PNG file. SVG files aren't supported.
