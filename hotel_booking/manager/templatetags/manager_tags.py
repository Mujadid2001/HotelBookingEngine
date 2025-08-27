from django import template
register = template.Library()


from django.urls import reverse
from django.utils.safestring import mark_safe

@register.filter
def attr(obj, name):
    return getattr(obj, name)

@register.simple_tag(takes_context=True)
def sidebar_link(context, url_name, icon_class, link_text):
    request = context['request']
    current_url = request.path
    target_url = reverse(url_name)
    is_active = current_url == target_url
    active_class = 'active' if is_active else ''

    return mark_safe(f'''
        <a href="{target_url}" class="list-group-item list-group-item-action {active_class}">
            <i class="fa-solid {icon_class} me-2"></i> {link_text}
        </a>
    ''')
