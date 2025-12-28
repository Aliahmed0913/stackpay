import pytest
from transactions.services.transaction_orchestration import create_transaction

@pytest.mark.django_db
def test_orchestration_transaction(mocker,customer_factory):
    validated_data = {'amount':100.22}
    customer = customer_factory()
    # replace paymob class with mock to prevent actual calls 
    mock_paymob = mocker.patch('transactions.services.transaction_orchestration.PayMob')
    # configure mock methods and return values
    instance = mock_paymob.return_value
    instance.create_order.return_value = 'paymob-id2232'
    instance.payment_key_token.return_value = 'test-paymob-token-in-transaction-creation'
    # call the provider orchestration function
    transaction = create_transaction(customer,validated_data)
    
    assert transaction.customer == customer
    assert transaction.payment_token == 'test-paymob-token-in-transaction-creation'
