import re

from django.core.exceptions import ValidationError

HEX_COLOR_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?$")


def validate_hex_color(value: str) -> None:
    """Validate that a string is a 6- or 8-digit hex color code.

    The optional trailing 2 digits are the alpha channel (e.g. #007b74
    or #007b7480 for 50% opacity).
    """
    if not HEX_COLOR_PATTERN.match(value):
        msg = "Enter a valid hex color code, e.g. #007b74 or #007b7480."
        raise ValidationError(msg)


def validate_regex_pattern(pattern: str) -> None:
    """Validate that a regex pattern is syntactically correct."""
    if not pattern:
        return
    try:
        re.compile(pattern)
    except re.error as e:
        msg = "Invalid regex pattern"
        raise ValidationError(msg) from e


DANGEROUS_REGEX_PATTERNS = [
    # Nested quantifiers: (x+)+, (x*)+, (x+)*, (x*)*
    # Catches: (a+)+, (.*)+, (\d*)*, etc.
    (
        r"\([^)]*[+*][^)]*\)[+*?]|\([^)]*[+*][^)]*\)\{",
        "Nested quantifiers (e.g., (a+)+ or (.*)+) are not allowed as they can "
        "cause excessive backtracking.",
    ),
    # Adjacent wildcards: .*.*  .+.+ .*.+
    (
        r"\.\*\.[\*\+]|\.\+\.[\*\+]",
        "Adjacent wildcards (e.g., .*.* or .+.+) are not allowed as they can "
        "cause excessive backtracking.",
    ),
    # Quantified backreference: (.+)\1+
    (
        r"\\[1-9][+*]|\{\\[1-9]\}[+*]",
        "Quantified backreferences like (e.g., (.+)\\1+) are not allowed as "
        "they can cause excessive backtracking.",
    ),
]


def validate_safe_regex(pattern: str) -> None:
    """Validate regex syntax and reject known dangerous patterns.

    Blocks patterns that:
    - Have invalid syntax
    - Contain nested quantifiers (e.g., (a+)+)
    - Contain adjacent wildcards (e.g., .*.*)
    - Contain quantified backreferences (e.g., (.+)\\1+)

    Raises:
        ValidationError if regex pattern is invalid or unsafe.
    """
    if not pattern:
        return

    validate_regex_pattern(pattern)

    for dangerous_pattern, message in DANGEROUS_REGEX_PATTERNS:
        if re.search(dangerous_pattern, pattern):
            raise ValidationError(message)
