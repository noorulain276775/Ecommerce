from django.urls import path
from accounts.views import *
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name="user_registration"),
    path('login/', LoginView.as_view(), name="user_login"),
    path('change_password/' ,csrf_exempt(ChangePasswordView.as_view()), name='change-password'),

]