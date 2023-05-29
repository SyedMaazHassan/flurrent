from django.db import models
from authentication.models import User
import uuid

# python manage.py makemigrations
# python manage.py migrate
# python manage.py runserver

class Section(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return f'{self.name}'

class Subsection(models.Model):
    name = models.CharField(max_length=255)
    weight = models.IntegerField()
    multiplier = models.IntegerField(default=2)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return f'{self.name}'


class Question(models.Model):
    text = models.TextField()
    points = models.IntegerField()
    subsection = models.ForeignKey(Subsection, on_delete=models.CASCADE)

    # class Meta:
    #     ordering = ("subsection__section__id", "subsection__id")

    def __str__(self):
        return self.text
    

class SurveyResponse(models.Model):
    survey_id = models.UUIDField(default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True)
    is_completed = models.BooleanField(default=False)
    next_question_no = models.IntegerField(null=True, blank=True)

    def generate_score(self):
        score = 0
        total = 0
        all_records = Record.objects.filter(survey = self) #25
        for record in all_records: #let say question 2
            total += record.question.points #5
            if record.is_yes:
                score += record.question.points
        return int(score/total*100)

    def is_survey_completed(self):
        all_questions = Question.objects.all()
        all_records = Record.objects.filter(survey = self)
        return all_questions.count() == all_records.count()

class Record(models.Model):
    survey = models.ForeignKey(SurveyResponse, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_yes = models.BooleanField()
