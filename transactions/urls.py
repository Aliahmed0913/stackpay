from django.urls import path,include
from transactions.views import TransactionViewSet,TransactionView,PayMobWebHookView
from rest_framework.routers import DefaultRouter

app_name = 'transactions'
register = DefaultRouter()
register.register(r'transaction',TransactionViewSet,basename='transaction')

urlpatterns = [
    path('',include(register.urls)),
    path('webhook/',PayMobWebHookView.as_view(),name='transaction-webhook'),
    path('testpay-view/',TransactionView.as_view(),name='transaction-view')
]