from django import template

register = template.Library()

@register.filter
def formato_decimal(valor):
    try:
        numero = float(valor)
        return f"{numero:.2f}".replace('.', ',')
    except (ValueError, TypeError):
        return valor
