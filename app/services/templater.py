# app/services/templater.py
# -----------------------------------
# Simple Jinja environment for email HTML templates
# -----------------------------------
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)

def render_template(name: str, **ctx) -> str:
    tpl = env.get_template(name)
    return tpl.render(**ctx)
