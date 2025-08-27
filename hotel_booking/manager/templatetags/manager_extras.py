from django import template

register = template.Library()

@register.filter
def attr(obj, attr_name):
    """Return attribute value by name, supporting callables and None safely."""
    if obj is None or attr_name is None:
        return ''
    val = getattr(obj, attr_name, '')
    # call if callable
    try:
        return val() if callable(val) else val
    except Exception:
        return val

@register.filter
def status_color(status):
    """Return a bootstrap color class based on booking status."""
    if status == 'CONFIRMED':
        return 'success'
    if status == 'PENDING':
        return 'warning'
    if status == 'CANCELLED':
        return 'danger'
    return 'secondary'
