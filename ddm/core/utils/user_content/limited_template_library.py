from django import template


register = template.Library()

# Register template tags.
register.tag('for', template.defaulttags.do_for)
register.tag('if', template.defaulttags.do_if)
register.tag('ifchanged', template.defaulttags.ifchanged)
register.tag('regroup', template.defaulttags.regroup)

# Register template filters.
register.filter('date', template.defaultfilters.date, expects_localtime=True, is_safe=False)
register.filter('default', template.defaultfilters.default, is_safe=False)
register.filter('dictsort', template.defaultfilters.dictsort, is_safe=False)
register.filter('dictsortreversed', template.defaultfilters.dictsortreversed, is_safe=False)
register.filter('first', template.defaultfilters.first, is_safe=False)
register.filter('last', template.defaultfilters.last, is_safe=True)
register.filter('length', template.defaultfilters.length, is_safe=False)
register.filter('random', template.defaultfilters.random, is_safe=True)
register.filter('truncatechars', template.defaultfilters.truncatechars, is_safe=True)
register.filter('truncatewords', template.defaultfilters.truncatewords, is_safe=True)
