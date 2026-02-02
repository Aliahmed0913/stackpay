from django.urls import path, include
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from . import views

app_name = "users"

routers = DefaultRouter()
routers.register("profiles", views.UserProfileViewSet, basename="user_profile")
routers.register("verify-code", views.VerificationCodeViewSet, basename="verify_code")

urlpatterns = [
    path("", include(routers.urls)),
    path("sign-up/", views.UserRegistrationView.as_view(), name="registration"),
    path("login-view/", views.LoginView.as_view(), name="login_view"),
    path(
        "obtain-token/", views.CookieTokenObtainPairView.as_view(), name="obtain_token"
    ),
    path(
        "refresh-token/", views.CookieTokenRefreshView.as_view(), name="refresh_token"
    ),
    path(
        "refresh_block/",
        views.CookieTokenDisableTokenView.as_view(),
        name="refresh_disabled",
    ),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("logout/", TokenBlacklistView.as_view(), name="block_token"),
]
