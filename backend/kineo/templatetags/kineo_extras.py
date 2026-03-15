from django import template
from kineo.constants import HALL_NAMES

register = template.Library()


@register.filter
def hall_display(hall_number):
    """Повертає «Зал Назва» за номером (1→Зал Ілленко, 2→Зал Довженко, 3→Зал Параджанов)."""
    if hall_number is None:
        return ""
    name = HALL_NAMES.get(int(hall_number), str(hall_number))
    return f"Зал {name}"
