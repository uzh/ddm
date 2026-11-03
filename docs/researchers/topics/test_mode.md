# Testing your Project

While setting up your project, use the **Test Link** (in the Project Hub) 
to try it out, not the participation link.

The participation link remembers you, so you can only take part once (or always 
open it in an incognito tab). Each time you open it, you have to go through the 
whole study from the start, even if you only want to check one part, like the 
questionnaire. Your test answers would also be mixed in with those of real participants.

The Test Link avoids both problems: you can try out your project as often as 
you like, and your test runs are clearly marked as tests.

## The Test Link

<!-- TODO: screenshot missing - capture the "Test Link" row in the Project Hub's Overview section and add as img/test_link.png -->

Each project has its own **Test Link**, shown next to the regular Participant Link in the Project Hub's
_Overview_ section. It looks like your participant link with a `test` parameter appended, e.g.:

```
https://your-domain.com/project-slug/briefing/?test=<test-token>
```

Opening this link enters the test mode and always starts a **brand-new, flagged test run** - regardless of whatever
participant session your browser's cookies currently point to. There's no need to use a private/incognito
window or clear cookies between test runs; just revisit the Test Link.
While you're on any page of a test run, a **Test Mode banner** is shown at the top

!!! note "Sharing the Test Link"

    The token in the Test Link is a long, unguessable random string, but anyone who has the link can use it
    to generate test participants for your project. Only share it with people you trust to test the project
    with you.

### Regenerating the Test Link

If you've shared the link more widely than intended, click **Regenerate Test Link** to invalidate it. Once
regenerated:

- The old link stops working - anyone who still has it sees a "test link disabled" page instead of starting
  (or continuing) a run.
- Test runs already collected under the old link are **not deleted**. They remain in your project's data
  exactly as before (see [below](#test-runs-in-your-data-and-exports)).

## Jumping to a Specific Step or Page

Instead of clicking through the whole participation flow to check, say, the questionnaire, 
use the navigation options in the test banner - pick a step (and, for the
questionnaire, a page) from the dropdowns and click **Go**.

Jumping between steps/pages like this keeps using the **same** test run (so data you've already donated in
that run stays available) - it only starts a new one when you revisit the plain Test Link, or use the
banner's **Start new test run** button.

!!! info "Jumping flags the run as out of order"

    Reaching a step out of its normal order marks that test run accordingly - this affects whether it's
    included in exports by default, see below.

## Test Runs in Your Data and Exports

Every test run is clearly recorded as such, so it's never mistaken for a real participation. Still, a test
run you completed **start to finish, in order** behaves like a normal participant: it's useful for checking
that the whole flow and your data actually works, so it's **included by default** in:

- The Participation Overview download and the Donations/Responses API (see
  [Data Download](../data_center/data_download.md) and the [APIs topic](apis.md)).

A test run where you used the navigation options to jump ahead, on the other hand, 
has incomplete or out-of-order data and isn't meaningful for analysis - 
these runs are **excluded by default** from the same exports. If
you need to inspect them anyway (e.g., while debugging), the Donations and Responses API accept an
`include_broken_test_runs=true` URL parameter to include them.
