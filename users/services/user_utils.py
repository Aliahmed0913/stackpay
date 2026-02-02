import logging
from django.utils.timezone import now
from django.conf import settings
from rest_framework.response import Response
from ..models import VerificationCode

logger = logging.getLogger(__name__)


def remove_expired_code(limit=500):
    """Remove expired EmailCode records from DB in batches

    Arg:
    limit (int): number of record to delete per batch
    """
    logger.info({"event": "expired_codes_cleanupp start..."})
    while True:
        expired_code_ids = list(
            VerificationCode.objects.filter(expiry_time__lt=now()).values_list(
                "id", flat=True
            )[:limit]
        )

        if not expired_code_ids:
            break

        deleted_count, _ = VerificationCode.objects.filter(
            id__in=expired_code_ids
        ).delete()
        logger.info({"event": "expired_codes_cleanup", "deleted_count": deleted_count})
    logger.info({"event": "expired_codes_cleanup done"})


def set_refresh_token_cookie(response: Response):
    """
    Set refresh token in the response cookie

    :param response: Response object
    :param refresh_token: str, refresh token string
    """
    response.set_cookie(
        "refresh_token",
        response.data["refresh"],
        samesite=getattr(settings, "SESSION_COOKIE_SAMESITE", "Strict"),
        secure=getattr(settings, "SESSION_COOKIE_SECURE", False),
        httponly=getattr(settings, "SESSION_COOKIE_HTTPONLY", True),
        max_age=getattr(settings, "LIFETIME_SESSION", None),
    )
    logger.info({"event": "refresh token set in cookie"})
    return response


from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


def get_token_from_cookie(request):
    """
    Return RefreshToken object if there an refresh token in the request cookie
    ,error message if one exist

    :param request: POST request usually
    """
    ref_token = request.COOKIES.get("refresh_token")
    if not ref_token:
        logger.warning({"event": "no refresh token in cookie"})
        return None, "No refresh token in cookie"
    try:
        refresh = RefreshToken(ref_token)
        logger.info({"event": "refresh token obtained from cookie"})
        return refresh, None
    except TokenError:
        logger.warning({"event": "invalid or expired refresh token in cookie"})
        return None, "invalid or expired refresh token"
