from django.shortcuts import render, redirect
from .models import *
from faker import Faker
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import requests
from django.http import JsonResponse
import json


# Create your views here.
@login_required
def index(request):

    # checking if user has already started survey
    user_survey = SurveyResponse.objects.filter(user = request.user).first()
    if user_survey:        
        if user_survey.is_completed:
            return redirect("surveys:survey-report", survey_id=user_survey.survey_id, section='Policy')
        else:
            return redirect("surveys:single-question", survey_id=user_survey.survey_id, question_id=user_survey.next_question_no)

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


@login_required
def start_survey(request):
    all_questions = Question.objects.all().order_by("id")
    # new response result
    survey_response = SurveyResponse.objects.filter(user = request.user).first()
    if survey_response and survey_response.is_completed:
        return redirect("surveys:survey-report", survey_id=survey_response.survey_id, section='Policy')
    else:
        survey_response = SurveyResponse.objects.create(user = request.user)
    return redirect("surveys:single-question", survey_id=survey_response.survey_id, question_id=1)


def get_question_ids():
    all_question = Question.objects.all().order_by("id")
    return all_question

@login_required
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
                # generated report
                survey.generate_report()
                survey.is_completed = True
                survey.end_time = timezone.now()
                survey.save()

                # Update user survey isTaken
                user = survey.user
                user.is_survey_taken = True
                user.save()

                return redirect('surveys:survey-report', survey_id=survey_id, section='Policy')

    context = {
        'sections': Section.objects.all(),
        'page': 'survey',
        "question": question,
        "page_info": page_info,
        "percent": percent 
    }

    return render(request, "single-question.html", context)


def fetch_suggestions(request, survey_id, section):
    if not request.user.is_authenticated:
        return JsonResponse({'data':[], 'message': 'Not authenticated'}, status=200)

    survey = SurveyResponse.objects.get(survey_id = survey_id)
    section = Section.objects.get(name = section)
    all_records = Record.objects.filter(survey = survey).filter(is_yes = False, question__subsection__section = section)
    report = survey.generate_report()
    single_section_object = report.get_single_section_report(section)



    # # Define the API endpoint URL
    api_url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer 987987978979',
    }

    # Define the variables
    print(section)

    if all_records.count() == 0:
        return JsonResponse({'data':[], 'message': 'You are upto date for this IT section'}, status=200)

    if single_section_object.suggestions.count() != 0:
        return JsonResponse({'data':[], 'message': 'Suggestions already generated'}, status=200)

  
    question_list = ""
    for record in all_records:
        question_id = record.question.id
        question = record.question.text
        section_name = record.question.subsection.section.name
        sub_section_name = record.question.subsection.name
        user_response = "Yes" if record.is_yes else "No"
    
        question_list += f'''
        \n
        points = {record.question.points}
        question_id = {question_id}
        Question = {question}
        section name of this question = {section_name}
        sub section name of this question = {sub_section_name}
        user says "{user_response}"

        \n
        '''


    tip = {
        'points': 'points',
        'question_id': 'question id',
        'question': 'question text',
        'user_answer': 'user answer',
        'title': 'project Title',
        'section': 'Section name',
        'subsection': 'Subsection name',
        'description': 'project Description',
    }


    # Construct the prompt with variables
    prompt = f'''
    we have a platform, to check user organizations credibility, when user fills a form. and responds to a question, if he says 'NO' for a potential requirements of the industry, we suggest tips to be align with industry standard.
    
    
    {question_list}


    Write 1 project for each question provided with title and description with a tip which can help user to fulfill this requirement, so next he says "YES" to this question
    based on the written project suggestion, similar projects will be suggested to user, so he can get an idea of what service need to be purchased.
    Write just like a buyer is submitting a project on freelancing marketplace. and he is looking for a service provider or IT specialist to do this job.
    Just write valid json list containing json object, nothing else, i need to use your response in the code. No starting and ending explanation. Just json list in code block

    
    title text limit = 255
    description = a little bit long, 1 paragraph please

    format must be in valid json format, with proper quotes:
    {str(tip)}
    '''

    # Define the payload (data) for the API request
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': prompt}
        ]
    }
    # Make the API request
    response = requests.post(api_url, headers=headers, json=data)
    print(response)
    # Access the response data
    if response.status_code == 200:
        response_data = response.json()
        # Process the response data as needed
        result = response_data['choices'][0]['message']['content']
        print(result)
        loaded_list = json.loads(result)
        print(loaded_list)

        if isinstance(loaded_list, list):
            for suggestion in loaded_list:
                # creating new suggestion in database
                new_suggestion = Suggestion.objects.create(
                    question_id = suggestion['question_id'],
                    title = suggestion['title'],
                    description = suggestion['description']
                )

                # Registering suggestion to single section report object
                single_section_object.suggestions.add(new_suggestion)

        # ...
        return JsonResponse({'data': loaded_list, 'message': 'Suggestions have been created'}, status=200)
    else:
        # Handle the API request error
        # ...
        return JsonResponse({"error": "Something went wrong"}, status=400)


@login_required
def view_report(request, survey_id, section):
    section_name = section
    survey = SurveyResponse.objects.get(survey_id = survey_id)
    report = survey.generate_report()
    all_sections = Section.objects.all()
    all_sections_names = all_sections.values_list("name", flat=True)
    single_section_report = report.get_single_section_report(section_name)
    context = {
        'to_create_suggestions': "true" if single_section_report.suggestions.count() == 0 else "false",
        'single_section_report': single_section_report,
        'report': report,
        'section': section_name,
        'section_reports': report.get_section_report(),
        'page': 'survey',
        'survey': survey,
        'all_sections_names': list(all_sections_names)
    }

    return render(request, "survey-report.html", context)