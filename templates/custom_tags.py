from django import template

register = template.Library()


@register.filter
def add_style(field, css):
    return field.as_widget(attrs={'style': css})
