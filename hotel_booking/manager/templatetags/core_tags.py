from django.template import Library

register = Library()

@register.filter
def attr(obj, attr_name):
    return getattr(obj, attr_name)
