from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.db import transaction

# python manage.py makemigrations
# python manage.py migrate
# python manage.py runserver


class SkillCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=25,null=True, blank=True)
    image = models.ImageField(upload_to="skill_categories", blank=True)

    # Automatically generate a slug based on the name
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_skills(self):
        skills = Skill.objects.filter(categories=self)
        return skills

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    categories = models.ManyToManyField(SkillCategory)
    image = models.ImageField(upload_to='skills', blank=True)
    quiz_added = models.PositiveIntegerField(default=0)

    def get_related_skills(self):
        categories = self.categories.all()
        related_skills = Skill.objects.filter(categories__in=categories).distinct()
        return related_skills

    def __str__(self):
        return f'{self.name} ({self.quiz_added})' 
    

class Quiz(models.Model):
    DIFFICULTY_CHOICES = (
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    )

    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='quizzes')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    difficulty = models.CharField(max_length=6, choices=DIFFICULTY_CHOICES, default='medium')
    badge = models.OneToOneField('skills.Badge', null=True, blank=True, on_delete=models.SET_NULL)
    passing_score = models.PositiveIntegerField(default=75)
    
    def get_questions(self):
        questions = Question.objects.filter(quiz = self)
        return questions

    def __str__(self):
        return self.name
    

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.CharField(max_length=255)
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=255)

    def __str__(self):
        return self.question_text



class Attempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    percentage = models.FloatField(null=True, blank=True)
    score = models.CharField(max_length=20, null=True, blank=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(auto_now=True)
    is_report_generated = models.BooleanField(default=False)
    is_success = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def get_report(self):
        return {
            'is_success': self.is_success,
            'score': self.score,
            'percentage': self.percentage,
            'is_report_generated': self.is_report_generated
        }
    
    def provide_badge_to_user(self):
        # create wonBadge object
        new_won_badge = WonBadge.objects.create(
            user = self.user,
            attempt = self,
            badge = self.quiz.badge
        )

    def make_result(self, score, percentage):
        self.score = score
        self.percentage = percentage
        self.is_report_generated = True
        with transaction.atomic():
            if self.percentage >= self.quiz.passing_score:
                self.is_success = True
                self.provide_badge_to_user()
            self.save()

    def generate_report(self, questions, answers):
        total_points = questions.count()
        obtained_points = 0
        for question in questions:
            selected_answer = answers.get(f'question_{question.id}')
            question.selected_answer = selected_answer
            correct_answer = question.correct_option
            print("========================")
            if selected_answer and correct_answer == selected_answer:
                print("xxxxxxxxx  CORRECT  xxxxxxx")
                obtained_points += 1
                question.status = 1
            else:
                question.status = 0
            print("correct answer", correct_answer)
            print("Given answer", selected_answer)
            print("========================")
            
        score = f'{obtained_points} / {total_points}'
        percentage = round(obtained_points/total_points*100, 0)
        self.make_result(score, percentage)

        return {
            'questions': questions
        }
 
    def __str__(self):
        return f"{self.user} - {self.quiz} - {self.score}"



class Badge(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="badges")

    def __str__(self):
        return self.name
    


class WonBadge(models.Model):
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.user} / {self.attempt.quiz}"