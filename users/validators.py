import re
from rest_framework import serializers

PASSWORD_REGEX = re.compile(r'^[A-Z](?=.*[a-z])(?=.*\d)(?!.*\s).{7,14}$')
PHONE_NUMBER_REGEX = re.compile(r'^(\(?\+?[0-9]*\)?)?[0-9_\- \(\)]*$')

def validate_password(value):    
    if not PASSWORD_REGEX.fullmatch(value):
        raise serializers.ValidationError({
            'Error':'Password must be alphanumeric start with uppercase ,'
            'restricted in 8-15 long with no spaces'
            })
    return value

def validate_phone_number(value):    
        if not PHONE_NUMBER_REGEX.fullmatch(value):
            raise serializers.ValidationError(
                'only allowing for an international dialing code at the start, - and spaces'
                )
        return value