import pytest
from users.models import User
from rest_framework.test import APIClient

@pytest.fixture(scope='function')
def create_activate_user(db):
    def make_user(**kwargs):
        user = User.objects.create_user(
            username = kwargs.get('username','Aliahmed'),
            password = kwargs.get('password','Aliahmed091$'),
            role_management = kwargs.get('role_management',User.Roles.CUSTOMER),
            email = kwargs.get('email','example998@cloud.com'),
            is_active=kwargs.get('is_active',False)
          )
        user.is_active = True
        user.save(update_fields=['is_active'])
        return user
    return make_user

@pytest.fixture()
def authenticate_client(api_client,create_activate_user):
    user = create_activate_user()
    api_client.force_authenticate(user=user)
    return user

