from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(int(key), "")

@register.filter
def split_lines(text):
    return [line.strip() for line in text.split('\n') if line.strip()]