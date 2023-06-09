from django.contrib import admin
from .models import Report, SectionReport, Section, Subsection, Question, SurveyResponse, Record, Suggestion


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Subsection)
class SubsectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight', 'multiplier', 'section')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'points', 'subsection', 'section')

    def section(self, obj):
        return obj.subsection.section
    
    section.short_description = 'Section'


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_time', 'end_time', 'is_completed')


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ('survey', 'question', 'is_yes')

admin.site.register(Report)
admin.site.register(SectionReport)
admin.site.register(Suggestion)
