import pytest
from transactions.services.paymob import PayMob, PayMobServiceError
from customers.models import Customer, Address
from rest_framework import status
import requests
import string
from django.core.cache import cache
# import responses
CONNECTION_TIMEOUT = (5,15)
PAYMOB_AUTH_CACH_KEY = 'paymob_token_key'

@pytest.mark.django_db()
class TestPayMobService:
    def test_generate_id(self):
        id = PayMob.generate_id()
        hex_digits = id[4:]
        is_hex = all(n in string.hexdigits for n in hex_digits)
        assert id.startswith('ORD') and is_hex
        assert len(hex_digits) == 6
    
    def test_correct_currency(self,customer_factory):
        customer=customer_factory(username='Currency_return',email='Currency-return009@gmail.com')
        paymob = PayMob(customer,currency='fakeconditionfield',address='fieldfortest')
        currency,_ = paymob.country_native_currencies()
        assert currency == 'EGP'
    
    @pytest.mark.parametrize('have_address,country',[(False,None), # no main address raise error here
                                                     (True,'SD')]) # unsupported country raise error here
    def test_fail_currency(self,customer_factory,have_address,country):   
        customer=customer_factory(with_address=have_address,country=country)     
        paymob = PayMob(customer,currency='fakeconditionfield',address='fieldfortest')
        
        with pytest.raises(PayMobServiceError):
            paymob.country_native_currencies()
            
    def test_request_field(self,customer_factory,mock_post):
        customer = customer_factory(with_address=False)
        paymob = PayMob(customer,currency='fieldfortest',address='fieldfortest')
        mock_post.status_code = status.HTTP_200_OK
        mock_post.json.return_value = {'request_field':'success'}
        result = paymob._request_field(payload={'fake':'data'}
                                       ,endpoint='http://fake.paymob/api'
                                       ,requested_field='request_field'
                                       ,field_name='testcase')
        assert result == 'success'
    
    @pytest.mark.parametrize('status_code,return_value',[(status.HTTP_200_OK, {} ) # missing field
                                                         ,(status.HTTP_400_BAD_REQUEST,None)]) # http error
    def test_request_field_fail(self,customer_factory,status_code,return_value,mock_post):
        customer = customer_factory(with_address=False)
        paymob = PayMob(customer,currency='fieldfortest',address='fieldfortest')
        
        mock_post.status_code = status_code
        mock_post.json.return_value = return_value
        
        if status_code == status.HTTP_400_BAD_REQUEST:
            mock_post.raise_for_status.side_effect = requests.exceptions.HTTPError('Bad Request')
        with pytest.raises(PayMobServiceError):
            paymob._request_field(payload={'fake':'data'}
                                       ,endpoint='http://fake.paymob/api'
                                       ,requested_field='not_found'
                                       ,field_name='testfield')
    
        
        
            

