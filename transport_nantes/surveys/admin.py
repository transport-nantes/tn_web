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


class SurveyQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "survey",
        "question_title",
    )
    search_fields = (
        "survey__name",
        "question_title",
    )


admin.site.register(SurveyQuestion, SurveyQuestionAdmin)


class SurveyResponderAdmin(admin.ModelAdmin):
    list_display = ("liste", "tete_de_liste", "commune", "survey")
    list_filter = (
        "commune__commune",
        "survey__name",
    )
    search_fields = (
        "commune__commune",
        "survey__name",
    )


admin.site.register(SurveyResponder, SurveyResponderAdmin)


class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = (
        "survey_responder",
        "survey_question",
    )
    list_filter = (
        "survey_responder__commune__commune",
        "survey_responder__survey__name",
        "survey_question__question_title",
    )
    search_fields = (
        "survey_responder__commune__commune",
        "survey_responder__survey__name",
        "survey_question__question_title",
    )


admin.site.register(SurveyResponse, SurveyResponseAdmin)
