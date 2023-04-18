from django.urls import path, include
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required

app_name = 'org'
urlpatterns = [
    path('org/', home_view, name="home"),
    path('experts/<endorser_id>', endorser_profile_view, name="single-endorser"),
    path('projects/<project_id>', single_project_view, name="single-project"),
    path('projects/<project_id>/applications', received_applications_view, name="received-applications"),
    path('org/profile/<str:section>', login_required(OrgUserProfileView.as_view()), name="profile"),
    path(
        'projects/<project_id>/applications/<application_id>/approve', 
        login_required(ApplicationApproval.as_view()), 
        name="approve-application"
    ),
    path(
        'orders/placed',
        manage_orders_view,
        name="orders"
    ),
    path(
        'org/order/<order_id>',
        single_order_view,
        name="single-order"
    ),
    path(
        'org/order/<order_id>/complete',
        mark_as_complete,
        name='mark-as-complete'
    )
] 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

