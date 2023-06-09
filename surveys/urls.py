from django.urls import path
from django.conf import settings
from .views import *
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required


app_name = 'surveys'

urlpatterns = [
    path('survey', index, name='survey'),
    path('survey/start', start_survey, name='start-survey'),
    path('survey/<survey_id>/question/<int:question_id>', view_question, name='single-question'),
    path('survey/<survey_id>/<section>/report', view_report, name='survey-report'),
    path('survey/fetch-suggestions/<survey_id>/<str:section>', fetch_suggestions, name='fetch-suggestions'),
] 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
