from django.urls import path
from accounts.views import *

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name="user_registration"),
    path('login/', LoginView.as_view(), name="user_login"),
    path('forgot-password/', ForgotPasswordView.as_view(), name="forgot_password"),
    path('verify-otp/', VerifyOTPView.as_view(), name="verify_otp"),
    path('resend-otp/', ResendOTPView.as_view(), name="resend_otp"),
    path('reset-password/', ResetPasswordView.as_view(), name="reset_password"),
]