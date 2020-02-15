from django.contrib import admin

# Register your models here.
from .models import Survey, SurveyQuestion, SurveyResponder, SurveyResponse

admin.site.register(Survey)
admin.site.register(SurveyQuestion)
admin.site.register(SurveyResponder)
admin.site.register(SurveyResponse)
