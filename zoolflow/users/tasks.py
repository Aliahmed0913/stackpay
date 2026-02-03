import logging
from celery import shared_task, Task
from .services.user_utils import remove_expired_code

logger = logging.getLogger(__name__)


@shared_task(bind=True, queue="expired", max_retries=3)
def remove_expired_task(self: Task):
    """
    Celery backgroud task for clean up any expired EmailCode object;
    """
    try:
        logger.info({"Event": "Start cleaning useless code"})
        remove_expired_code()
        logger.info({"Event": "End with cleaning"})
    except Exception as exc:
        logger.exception({"Error": "Expired code cleaner failed!"})
        raise self.retry(exc=exc, countdown=60)
