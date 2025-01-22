from django.urls import path
from .views import *

app_name = "accounts"

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signin/', SignInView.as_view(), name='signin'),
    path('signout/', SignOutView.as_view(), name='signout'),
    path('verify/<str:code>/', MobileVerifyView.as_view(), name='verify'),
    path('change/mobile/<str:code>/', ChangeMobileView.as_view(), name='change-mobile'),
    path('re-token/<str:code>/', ReTokenView.as_view(), name='re-token'),
    ]