from django.urls import path, include
from .views import *
app_name = 'authentication'
urlpatterns = [
    path('login', login_view, name='login'),
    path('signup', signup_view, name='signup'),
    path('logout', logout_view, name='logout'),
]