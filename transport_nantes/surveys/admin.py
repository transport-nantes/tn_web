from django.contrib import admin

# Register your models here.
from .models import (
    Survey,
    SurveyCommune,
    SurveyQuestion,
    SurveyResponder,
    SurveyResponse,
)

admin.site.register(Survey)
admin.site.register(SurveyCommune)
admin.site.register(SurveyQuestion)
admin.site.register(SurveyResponder)
admin.site.register(SurveyResponse)
