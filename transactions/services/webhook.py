import logging
import hashlib,hmac
from transactions.models import Transaction as TXN
from django.db import transaction as db_transaction
from django.conf import settings

logger = logging.getLogger(__name__)

class WebhookServiceError(Exception):
    # Raised when Webhook handling fail or return invalid value
    def __init__(self, message, details=None):
        super().__init__(message)
        self.message = message
        self.details = details

class WebhookService:
    def __init__(self,merchant_id,transaction_id):
        self.transaction = TXN.objects.get(merchant_order_id=merchant_id)
        self.pending = self.transaction.state == TXN.TransactionState.PENDING
        self.transaction_id = transaction_id

    def handle_webhook(self,success,pending,is_refunded,message,response_code):
        if self.pending:
            is_pending = (message in ["AUTHENTICATION_UNAVAILABLE","AUTHENTICATION_PENDING"] and response_code == 'PROCEED')
            if is_refunded:
                self.webhook_transition(TXN.TransactionState.REFUNDED)
                return
            elif success:
                self.webhook_transition(TXN.TransactionState.SUCCEEDED)
                return
            elif pending or is_pending:
                self.webhook_transition(TXN.TransactionState.PENDING)
                return
            else:
                self.webhook_transition(TXN.TransactionState.FAILED)
                return
        return

    def webhook_transition(self,new_state):
        '''Update the transaction state and transaction_id based on returned webhook '''
        with db_transaction.atomic():
            tx = TXN.objects.select_for_update().get(id=self.transaction.id)
            tx.state = new_state
            tx.transaction_id = self.transaction_id
            tx.save(update_fields=['state', 'transaction_id'])
        logger.info(f'Transaction {tx.transaction_id} updated to {tx.state} state.')
                     
    
    def verify_hmac(self, received_hmac, data):
        concatenate_fields = str.join('',[
            str(data['amount_cents']),
            str(data['created_at']),  
            str(data['currency']),    
            str(data['error_occured']).lower(),
            str(data['has_parent_transaction']).lower(),
            str(data['id']),
            str(data['integration_id']),
            str(data['is_3d_secure']).lower(),
            str(data['is_auth']).lower(),
            str(data['is_capture']).lower(),
            str(data['is_refunded']).lower(),
            str(data['is_standalone_payment']).lower(),
            str(data['is_voided']).lower(),
            str(data['order']['id']),
            str(data['owner']),
            str(data['pending']).lower(),
            str(data['source_data']['pan']),
            str(data['source_data']['sub_type']),
            str(data['source_data']['type']),
            str(data['success']).lower(),
    ])
        encode_key,encode_fields = getattr(settings,'HMAC_SECRET_KEY').encode('utf-8'),concatenate_fields.encode('utf-8')
        calculate_hmac = hmac.new(encode_key,encode_fields,digestmod=hashlib.sha512).hexdigest()

        if not (hmac.compare_digest(calculate_hmac,received_hmac)):
            logger.warning('This callback doesn\'t belong to this process.')
            return False
        logger.info('HMAC verified success.')
        return True
    