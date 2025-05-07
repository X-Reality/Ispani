from django.urls import path

from ..views.authentication import CompleteRegistrationView, LoginView, LogoutView, SignUpView, VerifyOTPView,PasswordResetRequestView,PasswordResetConfirmView



urlpatterns = [
    # Authentication URLs
    path('signup/', SignUpView.as_view(), name='signup'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('complete-registration/', CompleteRegistrationView.as_view(), name='complete-registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),

]