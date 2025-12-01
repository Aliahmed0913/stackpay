import pytest
from transactions.services.transaction_orchestration import create_transaction
@pytest.mark.django_db
def test_orchestration_transaction(mocker,customer_factory):
    validated_data = {'amount':100.22}
    customer = customer_factory()
    mock_paymob = mocker.patch('transactions.services.transaction_orchestration.PayMob')
    mocker.patch('transactions.services.transaction_orchestration.PayMob.generate_id',return_value='ORD-3A2384')
    instance = mock_paymob.return_value
    instance.create_order.return_value = 'paymob-id2232'
    instance.payment_key_token.return_value = 'test-paymob-token-in-transaction-creation'
    
    transaction = create_transaction(customer,validated_data)
    
    assert transaction.customer == customer
    assert transaction.paymob_payment_token == 'test-paymob-token-in-transaction-creation'
