from django.db import models
from django.contrib.auth.models import AbstractUser 
from django.core.validators import RegexValidator
# Create your models here.

class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN='ADMIN','admin'
        STAFF='STAFF','staff'
        CUSTOMER='CUSTOMER','customer'
    role_management=models.CharField(max_length=10, choices=Roles.choices, default=Roles.CUSTOMER)
        
    email=models.EmailField(unique=True)
    password = models.CharField(max_length=15, validators=[
        RegexValidator(
            regex=r'(?-i)(?=^.{8,15}$)((?!.*\s)(?=.*[A-Z])(?=.*[a-z]))(?=(1)(?=.*\d)|.*[^A-Za-z0-9])^.*$',
            message='Password must be alphanumeric start with uppercase restricted in (8,15) character'
        )
    ])
   
    phone_number = models.CharField(max_length=20, unique=True, validators=[
        RegexValidator(
            regex=r'^(\(?\+?[0-9]*\)?)?[0-9_\- \(\)]*$',
            message='allowing for an international dialing code at the start and hyphenation and spaces'
            )
    ])
    
    def __str__(self):
        return self.username
    