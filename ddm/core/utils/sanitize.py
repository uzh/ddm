import nh3

# Basic inline-formatting tags only - no block elements, links, or media.
LABEL_ALLOWED_TAGS = {"span", "b", "strong", "i", "em", "u", "br", "sub", "sup"}

# `class` is the only attribute researchers may use, e.g. to apply one of
# the project's existing CSS classes for basic styling.
LABEL_ALLOWED_ATTRIBUTES = {"*": {"class"}}


def sanitize_label_html(value: str) -> str:
    """
    Sanitizes a question item/scale point label for safe `v-html` rendering
    in the participant-facing frontend.

    Only a small set of inline-formatting tags and the `class` attribute
    are kept; everything else (scripts, event handlers, `style`, and any
    tag/attribute not explicitly allowed) is stripped.
    """
    if not value:
        return value
    return nh3.clean(
        value,
        tags=LABEL_ALLOWED_TAGS,
        attributes=LABEL_ALLOWED_ATTRIBUTES,
        clean_content_tags={"script", "style"},
    )
