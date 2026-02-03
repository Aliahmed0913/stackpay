import logging
import phonenumbers
from datetime import date
from phonenumbers.phonenumberutil import NumberParseException
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from config.settings import ALLOW_AGE, CUSTOMER_NAME_LENGTH

logger = logging.getLogger(__name__)


def validate_customer_name(value: str):
    if not value[0].isupper():
        logger.warning("Customer name must start with uppercase letter")
        raise ValidationError(_("Name must start with an uppercase letter."))
    if len(value) < CUSTOMER_NAME_LENGTH:
        logger.warning(
            "Customer name must be more than {CUSTOMER_NAME_LENGTH} characters."
        )
        raise ValidationError(
            _(f"Name must be more than {CUSTOMER_NAME_LENGTH} characters.")
        )


def validate_phone(value: str):
    try:
        phonenumber = phonenumbers.parse(value)

        if not phonenumbers.is_possible_number(phonenumber):
            logger.warning("phone_number format is not possible.")
            raise ValidationError(_("Format is not possible"))

        if not phonenumbers.is_valid_number(phonenumber):
            logger.warning("phone_number not valid for specific region.")
            raise ValidationError(_("Not valid for specific region"))

    except NumberParseException:
        logger.warning("phone_number is missing or invalid international format.")
        raise ValidationError(_("Missing or invalid international format."))

    return str(
        phonenumbers.format_number(phonenumber, phonenumbers.PhoneNumberFormat.E164)
    )


def valid_age(value: date):
    today = date.today()
    if value >= today:
        logger.warning("Invalid date of birth")
        raise ValidationError(_("Invalid date of birth"))

    # check if the month,day for today is before birthday month,day return true(1) else false(0)
    age = (
        today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    )
    if age >= ALLOW_AGE:
        return value
    logger.warning("The customer is underage.")
    raise ValidationError(_("Customer too young"))
