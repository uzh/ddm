import colorsys


def adjust_lightness(hex_color: str, amount: float) -> str:
    """Lighten (amount > 0) or darken (amount < 0) a hex color.

    Shifts the color's HSL lightness by `amount`, a fraction in [-1, 1],
    clamped to stay within valid lightness bounds. An optional trailing
    2-digit alpha channel (e.g. #007b7480) is preserved unchanged - a
    derived hover/focus shade shouldn't alter transparency.
    """
    hex_color = hex_color.lstrip("#")
    rgb, alpha = hex_color[:6], hex_color[6:]
    r, g, b = (int(rgb[i : i + 2], 16) / 255 for i in (0, 2, 4))

    h, l, s = colorsys.rgb_to_hls(r, g, b)  # noqa: E741
    l = max(0.0, min(1.0, l + amount))  # noqa: E741
    r, g, b = colorsys.hls_to_rgb(h, l, s)

    return f"#{round(r * 255):02x}{round(g * 255):02x}{round(b * 255):02x}{alpha}"
