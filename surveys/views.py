from django.shortcuts import render, redirect
from .models import *
from faker import Faker
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.utils import timezone

# Create your views here.
@login_required
def index(request):

    # checking if user has already started survey
    user_survey = SurveyResponse.objects.filter(user = request.user).first()

    instructions = [
        "Click on the \"Take Survey\" button on the top of each page to start the survey.",
        "The survey has 5 sections: Policy, Compliance, Productivity, Communications, and User Devices. Each section has several sub-sections that are designed to evaluate your organization's performance in specific areas.",
        "Each sub-section has a weight assigned to it, which determines its importance in the overall scoring. There is also a multiplier assigned to each sub-section, which can be modified if needed.",
        "Each sub-section has a list of questions that are designed to evaluate your organization's performance in that area. Each question has a \"Yes\" or \"No\" answer.",
        "When you start the survey, one question will be displayed on the screen at a time. Answer each question honestly by selecting the appropriate answer option.",
        "If you need to take a break during the survey, you can do so by clicking the \"Save and Exit\" button. Your progress will be saved, and you can resume the survey from where you left off the next time you log in.",
        "Once you have answered all the questions, the survey will be scored automatically based on your answers. You will receive a score for each section and sub-section, which will give you an idea of how well your organization is performing in each area.",
        "You can review your results and take action to improve your organization's performance in areas where you scored lower."
    ]


    # policy = Section.objects.create(name='Policy')
    # compliance = Section.objects.create(name='Compliance')
    # productivity = Section.objects.create(name='Productivity')
    # communications = Section.objects.create(name='Communications')
    # user_devices = Section.objects.create(name='User Devices')



    context = {
        'page': 'survey',
        'instructions': instructions,

    }
    return render(request, 'survey_instructions.html', context)



def start_survey(request):
    all_questions = Question.objects.all()
    # new response result
    survey_response = SurveyResponse.objects.filter(user = request.user).first()
    if survey_response and survey_response.is_completed:
        return redirect("surveys:survey-report", survey_id=survey_response.survey_id)
    else:
        survey_response = SurveyResponse.objects.create(user = request.user)
    return redirect("surveys:single-question", survey_id=survey_response.survey_id, question_id=all_questions.first().id)


def get_question_ids():
    all_question = Question.objects.all().order_by("subsection__id")
    return all_question


def view_question(request, survey_id, question_id):
    minimum = 1
    maximum = 25
    questions = get_question_ids()
    page_info = None
    paginator = Paginator(questions, 1)
    survey = SurveyResponse.objects.get(survey_id = survey_id)
    question_page = paginator.page(question_id)
    percent = 0
    try:
        question_page = paginator.page(question_id)
        question = question_page.object_list[0]

        questions_list = list(questions)
        index_number = questions_list.index(question)

        print("=====")
        print(index_number)
        print("=====")

        # Modify the page information
        current_question_number = question_page.start_index()
        total_questions = paginator.count

        page_info = f"Question {current_question_number} of {total_questions}"
        print(page_info)
        percent = int((current_question_number - 1) / total_questions * 100)
        print(current_question_number, total_questions, percent)
    except:
        # If the provided question_id is out of range, redirect to a completion page
        return redirect('surveys:survey')


    if request.method == "POST":
        answer = request.POST.get("question")
        if answer and answer in ("yes", "no"):
            is_yes = True if answer == "yes" else False

            new_record = Record.objects.filter(survey=survey, question=question).first()
            if not new_record:
                new_record = Record(survey=survey, question=question)
            new_record.is_yes = is_yes
            new_record.save()

            if question_page.has_next():
                next_question_id = question_page.next_page_number()
            
                # Updating new question
                survey.next_question_no = next_question_id
                survey.save()

                return redirect('surveys:single-question', survey_id=survey_id, question_id=next_question_id)
            else:
                # if survey.is_survey_completed():
                survey.is_completed = True
                survey.end_time = timezone.now()
                survey.save()

                # Update user survey isTaken
                user = survey.user
                user.is_survey_taken = True
                user.save()

                return redirect('surveys:survey-report', survey_id=survey_id)

    context = {
        'sections': Section.objects.all(),
        'page': 'survey',
        "question": question,
        "page_info": page_info,
        "percent": percent 
    }

    return render(request, "single-question.html", context)


def view_report(request, survey_id):
    survey = SurveyResponse.objects.get(survey_id = survey_id)
    all_sections = Section.objects.all()
    all_sections_names = all_sections.values_list("name", flat=True)
    context = {
        'page': 'survey',
        'survey': survey,
        'all_sections_names': list(all_sections_names)
    }

    return render(request, "survey-report.html", context)