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
    points = models.FloatField()
    subsection = models.ForeignKey(Subsection, on_delete=models.CASCADE)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.text
    

def generate_percentage(obtained_score, total_score):
    return int(obtained_score/total_score*100)

def generate_grade(percentage):
    if percentage >= 90:
        return "A"
    elif percentage >= 80:
        return "B"
    elif percentage >= 70:
        return "C"
    elif percentage >= 60:
        return "D"
    else:
        return "F"


class BaseReportModel(models.Model):
    obtained_score = models.FloatField()
    total_score = models.FloatField()
    percentage = models.FloatField()
    grade = models.CharField(max_length=255)

    class Meta:
        abstract = True
    

class Suggestion(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    point_to_add = models.FloatField(null=True, blank=True)


class SectionReport(BaseReportModel):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    suggestions = models.ManyToManyField(Suggestion, related_name='section_report')

    def __str__(self):
        return f'{self.section.name} => {self.grade} ({self.percentage}%)'


class Report(BaseReportModel):
    section_reports = models.ManyToManyField(SectionReport, related_name='main_report')
    survey = models.OneToOneField('surveys.SurveyResponse', on_delete=models.CASCADE, related_name='report')

    def get_single_section_report(self, section_name):
        single_section = self.section_reports.filter(section__name = section_name).first()
        return single_section


    def get_section_report(self):
        # Show section report many to many fields into python dict, 
        # section name as key and section report as value
        report_dict = {
            'marks': [],
            'grades': [],
            'labels': [],
            'percentages': []
        }
        all_total_score = self.total_score
        for section_report in self.section_reports.all():
            report_dict['marks'].append(section_report.obtained_score) 
            report_dict['grades'].append(section_report.grade)
            report_dict['labels'].append(section_report.section.name)
            report_dict['percentages'].append(int(section_report.obtained_score/all_total_score*100))
        report_dict['percentages'].append(100-self.percentage)
        report_dict['labels'].append("Opportunity to improve")
        return report_dict
    

    def __str__(self):
        return f'{self.survey.survey_id} => {self.grade} ({self.percentage}%)'


class SurveyResponse(models.Model):
    survey_id = models.UUIDField(default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True)
    is_completed = models.BooleanField(default=False)
    next_question_no = models.IntegerField(null=True, blank=True)

    def generate_report(self):
        # check if report is already generated
        report_query = Report.objects.filter(survey = self).first()
        if report_query:
            return report_query

        all_sections = Section.objects.all()
        all_records = Record.objects.filter(survey = self)
        report = Report(survey = self, obtained_score=0, total_score=0, percentage=0, grade="F")
        report.save()
        all_total_score = 0
        all_obtained_score = 0

        for section in all_sections:
            obtained_score = 0
            total_score = 0
            all_section_records = all_records.filter(question__subsection__section = section)
            for record in all_section_records:
                total_score += record.question.points
                if record.is_yes:
                    obtained_score += record.question.points

            # All total score
            all_total_score += total_score
            all_obtained_score += obtained_score

            # Creating report object
            section_report = SectionReport(section = section, obtained_score = obtained_score, total_score = total_score)
            section_report.percentage = generate_percentage(obtained_score, total_score)
            section_report.grade = generate_grade(section_report.percentage)
            section_report.save()

            print(section_report.section.name, "generated")

            # registering section report to main report
            report.section_reports.add(section_report)

        # Updating main report
        report.obtained_score = all_obtained_score
        report.total_score = all_total_score
        report.percentage = generate_percentage(all_obtained_score, all_total_score)
        report.grade = generate_grade(report.percentage)
        report.save()

        # Report and section report generated
        return report

    def is_survey_completed(self):
        all_questions = Question.objects.all()
        all_records = Record.objects.filter(survey = self)
        return all_questions.count() == all_records.count()
    

class Record(models.Model):
    survey = models.ForeignKey(SurveyResponse, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_yes = models.BooleanField()
