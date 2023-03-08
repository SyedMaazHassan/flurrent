from django.urls import path, include
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required

app_name = 'core'
urlpatterns = [
    path('', home_view, name="home"),
    path('landing', landing_view, name="landing"),
    path('switch/<str:mode>', switch_mode, name="switch"),
    path('profile', profile_view, name="profile"),
    path('inbox', inbox_view, name="inbox")
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
