from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def stars(value):
    try:
        rating = float(value)
    except (TypeError, ValueError):
        rating = 0

    html = ''
    for i in range(1, 6):
        if rating >= i:
            html += '<span class="star-full">&#9733;</span>'
        elif rating >= i - 0.5:
            html += '<span class="star-half">&#9733;</span>'
        else:
            html += '<span class="star-empty">&#9734;</span>'
    return mark_safe(html)


@register.filter
def currency(value):
    try:
        return f'${float(value):,.2f}'
    except (TypeError, ValueError):
        return value
