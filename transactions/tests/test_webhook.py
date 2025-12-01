import pytest
from django.urls import reverse

@pytest.mark.django_db
class TestPayMobWebHookView:
    def test_recieved_hmac(self,api_client):
        recieved_hmac = '8cd9658e7234fe44365814fa53508c06ea2a9076d073e471cc9bdcb53ac2d009fd852e03218a47ab082a235b3f2e039f41a935b32e28bd12df151dd5708a97e5'
        payload = {'obj':{'pending': False,'id': 373906620,'amount_cents': 12353,'created_at': '2025-11-24T15:58:08.589528','currency': 'EGP','error_occured': False,'has_parent_transaction': False,'integration_id': 5306007,'is_3d_secure': True,'is_auth': False,'is_capture': False,'is_refunded': False,'success': True,'is_standalone_payment': True,'is_voided': False,'order': {'id': 422946804,'merchant_order_id': 'ORD-3E70A0',},'owner': 2045572,'source_data': {'pan': '0008','type': 'card','sub_type': 'MasterCard',}}}
        url = reverse('transactions:transaction-webhook') + f'?hmac={recieved_hmac}'
        response = api_client.post(url,data=payload,format='json')

        assert response.status_code == 200
        
        #commit the work