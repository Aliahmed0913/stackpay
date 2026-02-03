import logging
import secrets
from enum import Enum
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from ..models import VerificationCode, User
from config.settings import CODE_LENGTH

logger = logging.getLogger(__name__)


class VerificationError(Exception):
    pass


class CodeExpiredError(VerificationError):
    pass


class CodeNotFoundError(VerificationError):
    pass


class InvalidCodeError(VerificationError):
    pass


class VerificationCodeService:
    class VerifyCodeStatus(Enum):
        VALID = "valid"
        ACTIVE = "active"
        CREATED = "created"

    DEFAULT_EXPIRY = timedelta(minutes=10)

    def __init__(self, user_email):
        try:
            self.user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            logger.warning("Entered user email not found.")
            raise VerificationError("User not found")

    def create_code(self, expiry: timedelta = None):
        """
        Create a user new verify code

        expiry time to consume that code
        """
        # check if there is no active code for that user
        if not self.last_unused_code():
            with transaction.atomic():
                verification_code = VerificationCode.objects.create(
                    user=self.user,
                    code=self.generate_code(),
                    expiry_time=timezone.now() + (expiry or self.DEFAULT_EXPIRY),
                )

            logger.info("Code created.", extra={"user_email": self.user.email})
            transaction.on_commit(
                lambda: verification_code_mail_task.delay(verification_code.id)
            )

    def validate_code(self, received_code: str):
        """
        Check if there an active code for requested user and evaluate it with received_code.
        """
        verify_code = self.last_unused_code()

        if not verify_code:
            logger.warning("No active code.", extra={"user_email": self.user.email})
            raise CodeNotFoundError("User doesn't have a valid code.")

        if self.is_expired_code(verify_code):
            self.disable_code(verify_code)
            raise CodeExpiredError("User verify code has expired.")

        elif str(verify_code.code) == received_code:
            self.user.is_active = True
            self.user.save(update_fields=["is_active"])
            self.disable_code(verify_code)
            logger.info("Account activated", extra={"user_email": self.user.email})
            return self.VerifyCodeStatus.VALID, self.user

        logger.warning("this invalid code")
        raise InvalidCodeError("Entered code is invalid.")

    def recreate_code_on_demand(self):
        """Check if there is no active verify code for not activated user and generate new one."""
        last_code = self.last_unused_code()

        # check if the user has been verified before
        if self.user.is_active:
            logger.warning("user has verified or has active code.")
            return self.VerifyCodeStatus.ACTIVE

        # see if the code for that user is expired disable it and create new one
        elif self.is_expired_code(last_code):
            if last_code:
                self.disable_code(last_code)
            self.create_code()
            return self.VerifyCodeStatus.CREATED

        remaining = last_code.expiry_time - timezone.now()
        logger.info(
            "There is active code",
            extra={"remaining_time": f"{remaining.seconds // 60 }m"},
        )
        return self.VerifyCodeStatus.VALID

    def is_expired_code(self, code):
        # check if code expired time exceeded the current time
        if code.expiry_time <= timezone.now():
            logger.warning(
                "Verify code expired.", extra={"user_email": self.user.email}
            )
            return True

    def disable_code(self, code):
        """Marked code as used."""
        code.is_used = True
        code.save(update_fields=["is_used"])

    def last_unused_code(self):
        """Return lastly active code for specific user."""

        last_code = VerificationCode.objects.filter(
            user_id=self.user.id, is_used=False
        ).order_by("-created_at")
        if last_code.exists():
            return last_code.first()
        return None

    def generate_code(self):
        """
        Return numeric value of specified length (CODE_LENGTH)

        """
        min_value = 10 ** (CODE_LENGTH - 1)
        max_value = (10**CODE_LENGTH) - 1
        return secrets.randbelow(max_value - min_value + 1) + min_value
