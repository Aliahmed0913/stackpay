from django.urls import path
from transactions.views import TransactionAPIView,TransactionView,PayMobWebHookView
app_name = 'transactions'

urlpatterns = [
    path('webhook/',PayMobWebHookView.as_view(),name='transaction-webhook'),
    path('txn/',TransactionAPIView.as_view(),name='transaction-create'),
    path('testpay-view/',TransactionView.as_view(),name='transaction-view')
]