from django.db import transaction
from django.dispatch import receiver
from django.db.models.signals import post_save
from users.models import User
from users.services.verifying_code import VerificationCodeService
from notifications.services.verification_code import send_verification_code

@receiver(post_save, sender=User)
def handle_user_registeration_verify_code(sender, instance, created, **kwargs):
    '''
    Listener to user when any registeration event happen.
    
    it's create and mail an verify code'''
    if created :
        def on_commit():
            service = VerificationCodeService(instance.id)
            code = service.create_code()
            send_verification_code(code.id)
    
        transaction.on_commit(on_commit)