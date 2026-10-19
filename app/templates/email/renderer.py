from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape


EMAIL_TEMPLATE_DIR = Path(__file__).parent / "html"

env = Environment(
    loader=FileSystemLoader(EMAIL_TEMPLATE_DIR),
    autoescape=select_autoescape(["html", "xml"])
)


def render_email_template(template_name: str, **context):
    template = env.get_template(template_name)
    return template.render(**context)