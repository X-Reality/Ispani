from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from myapp.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
     path('signup/', SignUpView.as_view(), name='signup'),
    path('signin/', SignInView.as_view(), name='signin'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('edit_profile/', EditProfileView.as_view(), name='edit_profile'), 
]
