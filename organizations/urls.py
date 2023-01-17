from django.urls import path, include
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required

app_name = 'org'
urlpatterns = [
    path('org/', home_view, name="home"),
    path('endorsers/<endorser_id>', endorser_profile_view, name="single-endorser"),
    path('projects/<project_id>', single_project_view, name="single-project"),    
    path('org/profile/<str:section>', login_required(OrgUserProfileView.as_view()), name="profile"),
] 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

