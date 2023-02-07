import json

from bokeh.plotting import figure
from bokeh.embed import components

from django import template
from django.utils.safestring import mark_safe


register = template.Library()

figure_defaults = dict(
    toolbar_location='below',
    height=400,
    width=400
)

bar_plot_defaults = dict(
    color='navy',
    alpha=0.6,
    width=0.9
)


@register.simple_tag(takes_context=True)
def get_simple_bar_plot(context, x_data, bar_labels, figure_settings='{}', plot_settings='{}'):
    view = context.get('view', None)
    if view is None:
        return None

    figure_settings = json.loads(figure_settings)
    figure_settings = {**figure_defaults, **figure_settings}
    figure_settings['x_range'] = bar_labels

    plot_settings = json.loads(plot_settings)
    plot_settings = {**bar_plot_defaults, **plot_settings}

    bar_counts = [int(x) for x in x_data]

    try:
        plot = figure(**figure_settings)
        plot.vbar(x=bar_labels, top=bar_counts, **plot_settings)
        plot.toolbar.logo = None

        script, div = components(plot)
        view.extra_scripts.append(script)
        return mark_safe(div)

    except Exception as e:
        print(e)
        return None
