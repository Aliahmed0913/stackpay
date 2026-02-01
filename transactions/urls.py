from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet, TransactionView, PayMobWebHookView

app_name = "transactions"
register = DefaultRouter()
register.register(r"transaction", TransactionViewSet, basename="transaction")

urlpatterns = [
    path("", include(register.urls)),
    path("webhook/", PayMobWebHookView.as_view(), name="transaction_webhook"),
    path("testpay-view/", TransactionView.as_view(), name="transaction_view"),
]
