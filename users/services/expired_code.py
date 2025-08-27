from users.models import EmailCode
from django.utils.timezone import now
import logging
logger = logging.getLogger(__name__)

def remove_expired_code(limit=500):
    '''Remove expired EmailCode records from DB in batches
     
       Arg:
       limit (int): rate the limite of delete per batch
    '''
    while True:
        expired_code_ids = list(
            EmailCode.objects
            .filter(expiry_time__lt=now())
            .values_list('id',flat=True)[:limit]
            )
        
        if not expired_code_ids:
            break
        
        deleted_count, _ = EmailCode.objects.filter(id__in=expired_code_ids).delete() 
        logger.info({'event':'expired_codes_cleanup', 'deleted_count':{deleted_count}})
    