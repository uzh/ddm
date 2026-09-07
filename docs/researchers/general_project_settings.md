# General Project Settings

The general project settings are divided into four sections:

| Section                                                   | What it's for                                                                      |
|-----------------------------------------------------------|------------------------------------------------------------------------------------|
| [**Public Information**](#public-information)             | Information visible to participants, such as your contact details and project name |
| [**URL Parameter Extraction**](#url-parameter-extraction) | Retrieve information from URL parameters                                           |
| [**Redirect Configuration**](#redirect-configuration)     | Choose whether and where to redirect participants after data collection ends       |
| [**Branding**](#branding)                                 | Customize the participation interface with your own colors and logo                |


## Public Information

This information is visible to your participants and helps them understand and trust your study.

| Setting                     | What it's for                                                                |
|-----------------------------|------------------------------------------------------------------------------|
| `Project Name`              | The name of the project shown in the participant's browser tab.              |
| `URL Identifier`            | How your participation URL looks like (e.g, www.ddm.url/**url-identifier**). |
| `Active`                    | Whether the project is (in)active                                            |
| `Contact Information`       | Your contact details - always accessible for participants.                   |
| `Data Protection Statement` | Your data protection statement - always accessible for participants.         |


??? setting-details "Setting Details"

    ---

    #### `Project Name`
    
    The name of the project shown in the participant's browser tab.
    
    ---

    #### `URL Identifier`
    
    A string used in the link your participants will use to take part in your study 
    - for example, www.ddm.url/**url-identifier**.
    
    !!! info "Allowed characters"
        Can only contain letters, numbers, hyphens, and underscores.
    
    ---

    #### `Active`
    
    Controls whether participants can currently join your project.

    When active, participants can take part using your project's URL. 
    When inactive, participants who open the link see an information page explaining 
    that participation isn't currently possible.
    
    ---

    #### `Contact Information`
    
    Contact details of the researcher responsible for the project.
    
    Linked in the footer of the participation interface, so participants can see 
    who is responsible and potentially contact the team conducting the study at any 
    point during the data donation process.
    
    ---    

    #### `Data Protection Statement`
    
    Data protection statement that describes how the data is processed.
    
    The data protection statement is linked in the footer of the participation interface and can be viewed by participants
    at any stage of the data donation process.

---

## URL Parameter Extraction

You can optionally configure DDM to extract information from parameters passed with the URL 
when a participant accesses a project (e.g., `www.ddm.url/project-url/briefing?participant=ID123&channel=socialMedia`). 

Scenarios where URL parameter extraction is useful include:

- **Linking participants to external services:** If participants first fill out 
a *questionnaire in external survey software* (e.g., SoSciSurvey or Qualtrics), 
or are redirected to you by an *external recruitment partner*, the participant 
ID can be passed and linked to DDM (e.g., `www.ddm.url/project-url?participant=ID123`).
- **Tracking recruitment channels:** If you recruit through different channels (e.g., social 
media, e-mail, and leaflets), URL parameters could be used to identify where 
participants are coming from (e.g., `www.ddm.url/project-url?channel=email`).

| Setting                            | What it's for                                                              |
|------------------------------------|----------------------------------------------------------------------------|
| `URL parameter extraction enabled` | Whether URL parameters are extracted when participants access the project. |
| `Expected URL parameter`           | Which parameter(s) to extract from the URL.                                |

??? setting-details "Setting Details"

    ---

    #### `URL parameter extraction enabled`
    
    Enable or disable whether URL parameters should be extracted when participants 
    access the project's briefing page.
    
    ---

    #### `Expected URL parameter`
    
    A string containing the parameter(s) that should be extracted. Separate multiple 
    parameters with semicolons (e.g., `parameter_A;parameter_B`).

    The extracted values are saved for each participant and included in the data 
    export. If a parameter isn't present in the URL, it's saved as `None`. Any other 
    parameters passed in the URL are ignored.

---

## Redirect Configuration

Participants can optionally be redirected to another website from the debriefing page.

Scenarios where redirecting participants at the end of their participation is useful
include:

- **Linking participants to external services:** If participants must complete a
*post-donation survey in external survey software* (e.g., SoSciSurvey or Qualtrics),
or should be redirected to a recruitment partner's callback URL, you can configure
the redirect to pass the participants ID to the redirect URL 
(e.g., `https://redirect.url?participant={{ participant_id }}`)
- **Redirecting to your website:** You may want to redirect your participants 
to your project's website.

| Setting            | What it's for                                                      |
|--------------------|--------------------------------------------------------------------|
| `Redirect enabled` | Whether participants are redirected after completing your project. |
| `Redirect address` | The URL participants are redirected to.                            |

??? setting-details "Setting Details"

    ---

    #### `Redirect enabled`
    
    Enable or disable redirecting participants after they've completed your project. 
    If enabled, a redirect button is shown on the data donation end page, linking to 
    the URL defined in `Redirect address`.
    
    ---

    #### `Redirect address`
    
    The URL participants are redirected to. Only required if `Redirect enabled` is enabled.
    
    !!! tip

        The redirect URL can include information about the participant and the 
        project, using variables that are populated automatically. Currently 
        supported: `{{ participant_id }}` for the participant ID and 
        `{{ project_id }}` for the project ID.

        For example: `https://redirect.url?participant={{ participant_id }}&project={{ project_id }}`

        See [this section](topics/templating_features.md) for more on variable inclusion.

---

## Branding

Customize the appearance of your donation project — provide up to two logos and set 
the colors used throughout the participation interface.

| Setting              | What it's for                                     |
|----------------------|---------------------------------------------------|
| `Show project title` | Whether the project title is shown in the header. |
| `Primary Color`      | Accent color for buttons and highlights.          |
| `Background Color`   | Background color of the participation interface.  |
| `Header Image Left`  | Logo shown on the left side of the header.        |
| `Header Image Right` | Logo shown on the right side of the header.       |

??? setting-details "Setting Details"

    ---

    #### `Show project title`
    
    If enabled, the project title is shown in the header of the participation interface.
    
    ---

    #### `Primary Color`
    
    Accent color used for buttons and highlights in the participation interface. 
    Lighter and darker shades are derived automatically — use a darker color here.
    
    ---
    
    #### `Background Color`
    
    Background color of the participation interface pages. Use a very light color here.
    
    ---

    #### `Header Image Left`
    
    An image displayed on the left side of the project header (e.g., an institution 
    or project logo).
    
    ---

    #### `Header Image Right`
    
    An image displayed on the right side of the project header (e.g., an institution 
    or project logo).

    !!! info "Accepted image formats"

        You can use standard file formates such as `JPEG`or `PNG` as header images.
        `SVG` images are not allowed.
