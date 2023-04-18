from django.contrib import admin
from .models import *
# Register your models here.

class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'icon', 'image']
    list_editable = ['icon']



class QuestionInline(admin.TabularInline):
    model = Question
    extra = 3

class QuizAdmin(admin.ModelAdmin):
    list_display = ('name', 'skill', 'difficulty')
    inlines = [QuestionInline]

admin.site.register(Quiz, QuizAdmin)
admin.site.register(Skill)
admin.site.register(Attempt)
admin.site.register(Badge)
admin.site.register(WonBadge)
admin.site.register(SkillCategory, SkillCategoryAdmin)