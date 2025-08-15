from django.urls import path
from .views import UserRegisterationViewset
urlpatterns = [
    path('register',UserRegisterationViewset.as_view({'post':'create'}))
]