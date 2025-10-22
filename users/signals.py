from django.db import transaction
from django.dispatch import receiver
from django.db.models.signals import post_save

from users.models import User
from users.services.verifying_code import VerificationCodeSerivce 

@receiver(post_save, sender=User)
def handle_user_registeration_verify_code(sender, instance, created, **kwargs):
    '''
    Listener to user when any registeration event happen.
    
    it's create an verify code'''
    if created :
        def on_commit():
            service = VerificationCodeSerivce(instance.email)
            service.create_code()
    
        transaction.on_commit(on_commit)