import logging
from celery import shared_task
from zoolflow.users.models import VerificationCode

logger = logging.getLogger(__name__)

#verification code email task and transaction state email task
   

# clean up expired code after hour