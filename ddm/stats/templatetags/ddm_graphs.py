# TODO: Create custom template tags that can be used to generate Bokeh graphs
from bokeh.plotting import figure
from bokeh.embed import components

from django import template


register = template.Library()


@register.simple_tag
def get_circle_plot(some_argument):
    plot = figure(width=400, height=400)
    # add a circle renderer with a size, color, and alpha
    plot.circle([1, 2, 3, 4, 5], [6, 7, 2, 4, 5], size=20, color="navy", alpha=0.5)
    script, div = components(plot)
    return {'div': div, 'script': script}
