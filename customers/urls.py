
from django.urls import path, include
from customers.views import CustomerProfile,CustomerAddress
from rest_framework.routers import DefaultRouter

app_name = 'customers'

customer_address = DefaultRouter()
customer_address.register('address',CustomerAddress,basename='customer_address')

urlpatterns = [
    path('profile/',CustomerProfile.as_view()),
    path('',include(customer_address.urls)),
]
