from django.template import Context, Template
from django.template.engine import Engine
from django.utils.safestring import SafeString


class TestEngine(Engine):
    default_builtins = ['ddm.core.utils.user_content.limited_template_library']


def preprocess_user_content(content: str) -> str:
    """
    Helper function to convert numeric html codes to characters to ensure the functionality of the custom
    templating features.
    """
    if not content:
        return ''

    content = content.replace('&gt;', '>')
    content = content.replace('&lt;', '<')
    return content


def render_user_content(content: str, context: dict=None) -> SafeString:
    """
    Function to render user provided content (used, e.g., to render a project's question text or debriefing text).

    Provides users (researchers) the flexibility to use a limited set of template tags to include variables and
    conditionals in their content.
    """
    content = preprocess_user_content(content)
    template = Template(content, engine=TestEngine())
    rendered_content = template.render(Context(context))
    return rendered_content
