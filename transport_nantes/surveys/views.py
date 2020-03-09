from django.views.generic.base import TemplateView
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Survey, SurveyQuestion, SurveyCommune, SurveyResponder, SurveyResponse

class MainSurveyView(TemplateView):
    template_name = 'surveys/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class CommuneChooserSurveyView(TemplateView):
    template_name = 'surveys/survey.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        responders = SurveyResponder.objects.filter(
            survey_id=kwargs['survey_id'])
        context['communes'] = set([responder.commune for responder in responders])
        context['listes'] = None;
        context['questions'] = None;
        return context

class ListeChooserSurveyView(CommuneChooserSurveyView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['this_commune'] = SurveyCommune.objects.filter(
            id=kwargs['commune_id'])[0]
        responders = SurveyResponder.objects.filter(
            survey_id=kwargs['survey_id'], commune=kwargs['commune_id'])
        context['listes'] = responders
        return context

class QuestionChooserSurveyView(ListeChooserSurveyView):
    def get_context_data(self, **kwargs):
        print(kwargs)
        context = super().get_context_data(**kwargs)
        context['this_liste'] = SurveyResponder.objects.filter(
            survey_id=kwargs['survey_id'],
            commune=kwargs['commune_id'],
            id=kwargs['responder_id'])[0]
        context['questions'] = SurveyQuestion.objects.filter(
            survey=kwargs['survey_id'])
        if 'question_id' in kwargs:
            context['this_question'] = SurveyQuestion.objects.filter(
            id=kwargs['question_id'])[0]
        print(context)
        return context

class ResponseDisplaySurveyView(QuestionChooserSurveyView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #### Make some responses, then make this work.
        return context

"""
Steps:

* The further pages should all use the same template.
  * Their views should provide empty lists and empty strings for not-yet-chosen
  * They should recover the survey name from the db.
  * There should be a candidate link.

* Then deploy to staging.
"""
