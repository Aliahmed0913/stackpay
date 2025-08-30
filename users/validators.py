from django.core.exceptions import ValidationError
import string
from django.utils.translation import gettext as _
import phonenumbers
from rest_framework import serializers
from phonenumbers.phonenumberutil import NumberParseException

class PasswordCustomValidator:
    def validate(self, password:str, user=None):
        length = len(password)
        first_char = password[0]
        if length > 15 or length < 8 :
            raise ValidationError(_('Length of password must be between 8-15 characters.'),code='Password_length')
        
        if not first_char.isupper():
            raise ValidationError(_('password must start with uppercase letter.'),code='Password_no-uppercase_start')
        
        if not any(c.islower() for c in password):
            raise ValidationError(_('Password must contain at least lowercase letter.'),code='Password_no_lowercase')
        
        if not any(c.isdigit() for c in password):
            raise ValidationError(_('Password must contain digit.'),code='Password_no_digit')
        
        if ' ' in password:
            raise ValidationError(_('Password can\'t contain spaces'),code='Password_contain_spaces')
        
        if not any(c in string.punctuation for c in password):
            raise ValidationError(_('Password must contain at least one special character.'),code='Password_no_special-character')
        
    def get_help_text(self):
        return _(
                'Password must be 8-15 length,'
                'start with uppercase, contain one lowercase at least,'
                'no spaces and contain at least one special character.'
                )     


class PhoneNumberValidator:
    def __init__(self, country_field=None):
        self.country_field = country_field
    
    def __call__(self, value, serializer_field):
        country = None
        if self.country_field:
            country_value = serializer_field.parent.initial_data.get(self.country_field)
            country = country_value.upper() if country_value else None
        
        try:
            phonenumber = phonenumbers.parse(value,country)
        
            if not phonenumbers.is_possible_number(phonenumber):
                raise serializers.ValidationError({'phone_number':'Format is not possible'})
        
            if not phonenumbers.is_valid_number(phonenumber):
                raise serializers.ValidationError({'phone_number':'Not valid for specific region'})
        except NumberParseException:
            raise serializers.ValidationError({'phone_number':'Missing or invalid region/format'})