from django.urls import path
from ..views.authentication import CompleteRegistrationView, LoginView, LogoutView, SignUpView, VerifyOTPView,ForgotPasswordView,ResetPasswordView,DeleteAccountView,SwitchRoleView

urlpatterns = [
    # Authentication URLs
    path('signup/', SignUpView.as_view(), name='signup'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('complete-registration/', CompleteRegistrationView.as_view(), name='complete-registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("switch-role/", SwitchRoleView.as_view(), name="switch-role"),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('account/delete/', DeleteAccountView.as_view(), name='account-delete'),
]