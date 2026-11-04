# Export & Copy

Reuse a project's configuration - its file uploaders, blueprints, and questionnaire - for a
new study, instead of rebuilding it from scratch. Collected data is never included in either
action.

<!-- TODO: screenshot missing - capture the "Export & Copy" section of the Project Hub and add as img/export_copy.png -->

You can access these options in _Project Hub > Export & Copy_.

## Copy a Project

Click **Copy Project** to duplicate the project - including all its uploaders, blueprints,
and questions - into a brand-new project. Review the suggested name and URL identifier (DDM
proposes `<name> (copy)` and `<slug>-copy`) before confirming.

## Export a Project

Click **Export Project** to download the project's configuration as a JSON file.

## Import a Project

From your [project list](create_project.md#project-list), click **Import Project**, upload a
previously exported JSON file, then review and confirm the new project's name and URL
identifier.

!!! tip "Moving a project between DDM instances"

    Export and import together let you move a project's configuration to a different DDM
    instance - for example, from a test/staging server to your production server.
