from django.urls import path, include
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required

app_name = 'skills'
urlpatterns = [
    path('add_skills', add_skill_view, name="add_skills"),

    path('skills', skill_view, name="skill_list"),
    path('skills/<int:skill_id>', skill_detail_view, name="single_skill"),

    path('skills/<int:skill_id>/quiz/<int:quiz_id>/instructions', quiz_instructions_view, name="quiz_instructions"),
    path('skills/<int:skill_id>/quiz/<int:quiz_id>/start', quiz_start_view, name="quiz_start"),
    # path('skills/<int:skill_id>/quiz/<int:quiz_id>/submit', quiz_submit_view, name="quiz_submit"),

    path('attempts/<int:attempt_id>/quiz', main_quiz_view, name="quiz"),

    path('attempts/<int:attempt_id>/done', quiz_result_view, name="quiz_result"),


] 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

