from users.models import User
import pytest
from customers.models import Customer, Address

@pytest.fixture()
def customer_factory(db):
  def create_customer(with_address=True,**kwargs):
    user =  User.objects.create_user(
                        username = kwargs.get('username','Aliahmed'),
                        password = kwargs.get('password','Aliahmed091$'),
                        role_management = kwargs.get('role_management',User.Roles.CUSTOMER),
                        email = kwargs.get('email','example998@cloud.com'),)
    customer = Customer.objects.create(user=user)
    
    if with_address:
        Address.objects.create(customer=customer,main_address=kwargs.get('main_address',True),
                              country=kwargs.get('country','EG'))
    
    return customer
  return create_customer

@pytest.fixture
def mock_post(mocker):
    mock_post = mocker.patch('transactions.services.paymob.requests.post')
    mock_response = mocker.Mock()
    mock_post.return_value = mock_response
    return mock_response



