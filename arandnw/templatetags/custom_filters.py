from django import template

register = template.Library()

WORDS = ['лесом','нафнаф', 'big', 'sometitle']

@register.filter(name='Censor')
def Censor(value):
    if not isinstance(value, str):
        raise ValueError('Нельзя цензурировать не строку')

    for word in WORDS:
        value = value.replace(word[1:], '*' * (len(word) - 1))
    return value