import logging
from django.db import transaction as db_transaction
from .paymob import PayMob, ProviderServiceError
from ..models import Transaction
from .helpers import retrieve_transaction_for_update

logger = logging.getLogger(__name__)


class TransactionOrchestrationServiceError(Exception):
    # Raised when orchestration handling fail or return invalid value
    def __init__(self, message, details=None):
        super().__init__(message)
        self.message = message
        self.details = details


class TransactionOrchestrationService:
    def __init__(self, customer):
        self.customer = customer

    def create_transaction(self, validated_data):
        """
        Create transaction with approbiate filed,
        after interacting with payment provider
        """
        logger.info(
            (
                f"Initiate transaction for customer with ID {self.customer.id} amount {validated_data['amount']}"
            ).replace("\n", "")
        )
        with db_transaction.atomic():
            transaction = Transaction.objects.create(
                customer=self.customer,
                **validated_data,
            )
        logger.info(
            (
                f"Transaction {transaction.merchant_order_id} created successfully."
            ).replace("\n", "")
        )
        # Interact with provider to create order and payment token on commit
        db_transaction.on_commit(
            lambda: self._interact_with_provider(transaction),
        )
        transaction.refresh_from_db()
        return transaction

    def _interact_with_provider(self, transaction: Transaction):
        """
        Interact with PayMob to create order and payment keym
        and set them in transaction passed object
        """
        merchant_id = transaction.merchant_order_id
        provider = PayMob(customer=self.customer, merchant_id=merchant_id)
        amount_cents = int(transaction.amount * 100)
        try:
            # Create order and payment key token with provider
            # Return order id and payment token
            provider_id = provider.create_order(amount_cents)
            payment_token = provider.payment_key_token(
                provider_id=provider_id, amount_cents=amount_cents
            )
            # Update transaction fields with provider returned values
            TransactionOrchestrationService._define_provider_attribute(
                transaction, provider_id, payment_token
            )
        except ProviderServiceError as e:
            with db_transaction.atomic():
                tx = retrieve_transaction_for_update(id=transaction.id)
                tx.state = Transaction.TransactionState.FAILED
                tx.save(update_fields=["state"])
                print("Transaction marked as FAILED due to provider error.")
            logger.error(
                f"Transaction {merchant_id} failed during provider interaction: {e.message}"
            )
            raise TransactionOrchestrationServiceError(
                details="Provider interaction failed", message=e.message
            )

    @staticmethod
    def _define_provider_attribute(transaction, provider_id, payment_token):
        """
        Set provider related fields in transaction instance
        """
        with db_transaction.atomic():
            tx = retrieve_transaction_for_update(id=transaction.id)
            tx.order_id = provider_id
            tx.payment_token = payment_token
            tx.state = Transaction.TransactionState.PENDING
            tx.save(update_fields=["order_id", "payment_token", "state"])
            print("transaction updated with provider fields.")
        logger.info(f"Transaction {tx.merchant_order_id} updated with provider fields.")
