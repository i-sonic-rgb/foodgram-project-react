import base64

import webcolors
from django.core.files.base import ContentFile
from rest_framework import serializers


class Hex2NameColor(serializers.Field):
    '''Custom field - returns color name of HEX data (or "black")'''
    def to_representation(self, value):
        try:
            value = webcolors.hex_to_name(value)
        except ValueError:
            value = 'black'
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class Base64ImageField(serializers.ImageField):
    '''Custom field - saves base64 string as image.'''
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='image.' + ext)

        return super().to_internal_value(data)
