from django import template

from ddm.core.utils.color import adjust_lightness

register = template.Library()


@register.filter
def lighten(hex_color: str, amount: float) -> str:
    return adjust_lightness(hex_color, float(amount) / 100)


@register.filter
def darken(hex_color: str, amount: float) -> str:
    return adjust_lightness(hex_color, -float(amount) / 100)
