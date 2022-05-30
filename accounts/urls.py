from django.urls import path
from accounts.views import *

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name="user_registration"),
    path('login/', LoginView.as_view(), name="user_login"),

]