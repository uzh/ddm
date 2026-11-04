# Continuation

After participants request their data from a platform, it can take hours or days until
they can download it. With a continuation link, participants can leave the study and come
back later to upload their data.

## The Continuation Link

Each participant has their own continuation link:

```text
https://<your-ddm-server>/ddm/<url-identifier>/continue?p=<participant-id>
```

If the participant ID doesn't exist, participants see a page saying that continuation
failed, with the option to start a new participation.

## Show the Link to Participants

Add the link to your [instructions](../data_collection_configuration/datadonation/datadonation_configuration.md#instruction-configuration)
with the variable `{{ participant_id }}`, which DDM replaces with each participant's ID
(see [Dynamic Content](templating_features.md)). For example:

```django
It can take up to a few days until you can download your data. Save this link, for
example as a bookmark or by sending it to yourself by email, and use it to continue
when your data is ready:

https://your-ddm-server.example.org/ddm/my-study/continue?p={{ participant_id }}
```

!!! warning "Ask participants to keep the link private"

    Anyone with a participant's continuation link can continue that participation, without
    logging in. Ask participants not to share it.
