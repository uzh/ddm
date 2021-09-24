import re
from django import template
from ddm.models import Page
from ddm.tools import fill_variable_placeholder

register = template.Library()


@register.filter
def get_scale_loop(value):
    i = 1
    s = ''
    value = int(value) + 1
    for v in range(1, value):
        s += str(i)
        i += 1

    return s


@register.filter
def divide(value, arg):
    try:
        return int(value) / int(arg)
    except (ValueError, ZeroDivisionError):
        return None


@register.filter
def insert_variable_response(text, sub):

    new_text = fill_variable_placeholder(text, sub)

    return new_text


@register.filter
def get_list(key):

    l = []
    for i in range(0, int(float(key))):
        l.append(i)

    return l


@register.filter
def to_label(value):
    value = value.replace('_', ' ')
    return value.title()


@register.filter
def get_questions(page_id):
    page = Page.objects.get(id=page_id)
    questions = page.question_set.all()
    return questions
