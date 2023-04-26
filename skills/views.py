from django.shortcuts import render, redirect
from .models import *
from django.utils import timezone
from random import sample
import json
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def generate_quiz():
    # Create the quiz object
    skill = Skill.objects.get(id=2)
    quiz_name = 'Intermediate Python Quiz'
    quiz_description = 'This quiz consists of 10 questions that cover various Python concepts such as lists, strings, functions, and operators.'
    quiz_difficulty = 'Intermediate'
    quiz_passing_score = 75
    quiz = Quiz.objects.create(skill=skill, name=quiz_name, description=quiz_description, difficulty=quiz_difficulty, passing_score=quiz_passing_score)


    # Create the questions for the quiz
    questions = [
    {
        'question_text': 'What is the output of this code? x = [1, 2, 3] ; y = x ; y.append(4) ; print(x)',
        'option1': '[1, 2, 3]',
        'option2': '[1, 2, 3, 4]',
        'option3': '[1, 2, 4]',
        'option4': 'Error',
        'correct_option': '[1, 2, 3, 4]',
    },
    {
        'question_text': 'What is the output of this code? a = "Python" ; print(a[1:4])',
        'option1': 'yth',
        'option2': 'Pyt',
        'option3': 'thon',
        'option4': 'ytho',
        'correct_option': 'yth',
    },
    {
        'question_text': 'What is the output of this code? x = [1, 2, 3] ; y = x ; x = [4, 5, 6] ; print(y)',
        'option1': '[1, 2, 3]',
        'option2': '[1, 2, 3, 4, 5, 6]',
        'option3': '[4, 5, 6]',
        'option4': 'Error',
        'correct_option': '[1, 2, 3]',
    },
    {
        'question_text': 'What is the output of this code? a = "Python" ; b = "python" ; print(a == b)',
        'option1': 'True',
        'option2': 'False',
        'option3': 'Error',
        'option4': 'None of the above',
        'correct_option': 'False',
    },
    {
        'question_text': 'What is the output of this code? def foo(x, y): return x + y ; print(foo(2, 3))',
        'option1': '5',
        'option2': '6',
        'option3': '23',
        'option4': 'Error',
        'correct_option': '5',
    },
    {
        'question_text': 'What is the output of this code? a = [1, 2, 3, 4, 5] ; b = a[1:4] ; b[0] = 0 ; print(a)',
        'option1': '[1, 2, 3, 4, 5]',
        'option2': '[1, 0, 3, 4, 5]',
        'option3': '[0, 2, 3, 4, 5]',
        'option4': 'Error',
        'correct_option': '[1, 2, 3, 4, 5]',
    },
    {
        'question_text': 'What is the output of this code? a = [1, 2, 3] ; b = a ; a += [4, 5] ; print(b)',
        'option1': '[1, 2, 3, 4, 5]',
        'option2': '[1, 2, 3]',
        'option3': '[4, 5]',
        'option4': 'Error',
        'correct_option': '[1, 2, 3, 4, 5]',
    },
    {        
        'question_text': 'What is the output of this code? x = 10 ; y = 5 ; print(x % y)',        
        'option1': '2',        
        'option2': '0',        
        'option3': '1',        
        'option4': '5',        
        'correct_option': '0',    
    },    
    {        
        'question_text': 'What is the output of this code? x = [1, 2, 3] ; y = [4, 5, 6] ; print(x + y)',        
        'option1': '[1, 2, 3, 4, 5, 6]',        
        'option2': '[[1, 2, 3], [4, 5, 6]]',        
        'option3': '[5, 7, 9]',        
        'option4': 'Error',        
        'correct_option': '[1, 2, 3, 4, 5, 6]',    
    },    
    {        
        'question_text': 'What is the output of this code? a = [1, 2, 3, 4, 5] ; print(a.pop()) ; print(a)',        
        'option1': '5, [1, 2, 3, 4]',        
        'option2': '5, [1, 2, 3, 4, 5]',        
        'option3': '4, [1, 2, 3, 5]',        
        'option4': '4, [1, 2, 3, 4, 5]',        
        'correct_option': '5, [1, 2, 3, 4]',    
    }
    ]


    # Shuffle the questions and select 10 of them
    questions = sample(questions, 10)

    # Create the question objects and associate them with the quiz
    for i, question_data in enumerate(questions):
        Question.objects.create(
            quiz=quiz,
            question_text=question_data['question_text'],
            option1=question_data['option1'],
            option2=question_data['option2'],
            option3=question_data['option3'],
            option4=question_data['option4'],
            correct_option=question_data['correct_option'],
        )

        print("Question created", i)

    # Return the quiz object
    return quiz



# Create your views here.
@login_required
def skill_view(request):
    # generate_quiz()
    skill_categories = SkillCategory.objects.all()
    all_skills = Skill.objects.all()

    # Search functionality
    query = request.GET.get('q')
    if query:
        skill_categories = skill_categories.filter(name__icontains=query)
        all_skills = all_skills.filter(name__icontains=query)

    context = {
        'skill_categories': skill_categories,
        'all_skills': all_skills,
        'query': query
    }

    return render(request, "skill_list.html", context)

@login_required
def skill_detail_view(request, skill_id):
    # all related skills
    skill = Skill.objects.get(id = skill_id)
    category = skill.categories.all().first()

    # all won badges of current user
    all_quiz = Quiz.objects.filter(skill = skill)
    all_won_quiz_ids = Attempt.objects.filter(user = request.user, is_success = True).values_list("quiz__id", flat=True)
    # for quiz in all_quiz:

    # add temporary field is_won to each quiz object
    for quiz in all_quiz:
        quiz.is_won = True if quiz.id in all_won_quiz_ids else False

    context = {
        'skill': skill,
        'related_skills': skill.get_related_skills(),
        'category': category,
        'all_quiz': all_quiz
    }
    return render(request, "single_skill.html", context)

@login_required
def quiz_instructions_view(request, skill_id, quiz_id):
    instructions = [
        "Please ensure that you are in a quiet and distraction-free environment before starting the quiz.",
        "Do not use any external resources or aids during the quiz. This includes textbooks, notes, calculators, or any other materials.",
        "The quiz is timed, so please make sure to manage your time wisely and answer all questions before the time runs out.",
        "Please read all questions and instructions carefully before answering.",
        "You will not be able to go back and change your answers, so make sure to review your answers before submitting.",
        "If you encounter any technical difficulties during the quiz, please contact the support team immediately.",
        "Cheating will not be tolerated and may result in disciplinary action.",
        "The quiz may have multiple sections or pages, so please make sure to navigate through all sections before submitting.",
        "Once you have submitted the quiz, you will not be able to access it again, so make sure you are ready before submitting.",
        "Good luck and we hope you enjoy the quiz!"
    ]
    quiz = Quiz.objects.get(id = quiz_id)

    # Check if already passed
    all_won_quiz_ids = Attempt.objects.filter(user = request.user, is_success = True).values_list("quiz__id", flat=True)
    if quiz.id in all_won_quiz_ids:
        messages.success(request, "You already passed this quiz and won the badge.")
        return redirect("skills:single_skill", skill_id=skill_id)

    skill = quiz.skill
    context = {
        'related_skills': skill.get_related_skills(),
        'category': skill.categories.all().first(),
        'skill': skill,
        'quiz': quiz,
        'instructions': instructions
    }
    return render(request, "quiz_instructions.html", context)

@login_required
def quiz_start_view(request, skill_id, quiz_id):
    quiz = Quiz.objects.get(id = quiz_id)

    # Create new attempt
    new_attempt = Attempt.objects.create(
        quiz = quiz,
        user = request.user
    )
    return redirect("skills:quiz", attempt_id=new_attempt.id)

@login_required
def main_quiz_view(request, attempt_id):
    attempt = Attempt.objects.get(id = attempt_id)
    if attempt.is_report_generated:
        return redirect("skills:quiz_result", attempt_id=attempt_id)

    quiz = attempt.quiz
    skill = quiz.skill
    questions = quiz.get_questions()

    if request.method == 'POST':
        answers = request.POST
        print(answers)
        result = attempt.generate_report(questions, answers)
        questions = result['questions']
                
    print("=========")
    print(attempt.is_report_generated)
    print("=========")

    context = {
        "report": attempt.get_report(),
        'attempt': attempt,
        'category': skill.categories.all().first(),
        'questions': questions,
        'skill': skill,
        'quiz': quiz,
    }
    return render(request, "quiz_start.html", context)


@login_required
def add_skill_view(request):
    output = {'status': False, 'message': None}
    if request.method == 'GET':
        skills = request.GET.get('skills')
        user = request.user
        endorser_profile = user.is_endorser
        if endorser_profile and skills:
            skills = json.loads(skills)
            skills = [int(x) for x in skills]

            previously_added_skills = endorser_profile.get_skills()
            skills = list(set(skills))
            endorser_profile.set_skills(skills)

            output['message'] = "Selected skills have been saved"
            output["status"] = True

    return JsonResponse(output)



@login_required
def quiz_result_view(request, attempt_id):
    attempt = Attempt.objects.get(id = attempt_id)
    quiz = attempt.quiz
    skill = quiz.skill
    context = {
        "report": attempt.get_report(),
        'attempt': attempt,
        'category': skill.categories.all().first(),
        'skill': skill,
        'quiz': quiz,
    }
    return render(request, "quiz_result.html", context)
