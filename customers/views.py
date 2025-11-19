from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import RetrieveUpdateDestroyAPIView,RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from customers.models import Customer, Address, KnowYourCustomer 
from customers.serializers import CustomerProfileSerializer, CustomerAddressSerializer, KnowYourCustomerSerializer
# Create your views here.

class CustomerProfileAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerProfileSerializer
    def get_object(self):
        return Customer.objects.get(user = self.request.user)    

class CustomerAddressViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerAddressSerializer
    def get_queryset(self):
        user = self.request.user
        addresses = Address.objects.filter(customer = user.customer_profile)
        return addresses

class KnowYourCustomerAPIView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = KnowYourCustomerSerializer
    def get_object(self):
        return KnowYourCustomer.objects.get(customer = self.request.user.customer_profile)

