
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')), 
    path('accounts/', include('allauth.urls')),
    
    # Authentication URLs
    path('auth/', include('myapp.urls.authentication')),
    
    # Group management
    path('groups/', include('myapp.urls.groups')),
    
    # Messaging
    path('chat/', include('myapp.urls.messaging')),
    
    # Events
    path('events/', include('myapp.urls.events')),
    
    # Tutoring system
    path('tutoring/', include('myapp.urls.tutoring')),
    
]

