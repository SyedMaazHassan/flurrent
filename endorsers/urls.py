from django.urls import path, include
from .views import *
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static


app_name = 'endorsers'
urlpatterns = [
    path("find-projects", home_view, name="home"),
    path('profile/<str:section>', login_required(EndorserUserProfileView.as_view()), name="profile"),
    path('', login_required(EndorserUserProfileView.as_view()), name="profile"),
    path('projects/<project_id>/apply', apply_on_project, name="apply-on-project"),    

    # path("endorser/<endorser_id>", endorser_profile_view, name="single-endorser")
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
