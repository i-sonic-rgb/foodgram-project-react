import re

from django.core.exceptions import ValidationError


def validate_username(value):
    '''Custom username validator. Except "me". Allowed: [a-zA-Z0-9_.@+-].'''
    if value == 'me':
        raise ValidationError(
            ('Запрещено использовать логин me!'),
            params={'value': value},
        )
    reg = re.compile(r'^[\w.@+-]+$')
    if not bool(re.fullmatch(reg, value)):
        raise ValidationError('Недопустимый символ в username.')
