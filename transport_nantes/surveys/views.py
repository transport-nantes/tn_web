from django.views.generic.base import TemplateView
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from .models import Survey, SurveyQuestion, SurveyCommune, SurveyResponder, SurveyResponse

# This currently does nothing useful, just says it doesn't know.
# It should show a list of active questionnaires.
class MainSurveyView(TemplateView):
    template_name = 'surveys/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

# Show the questionns for one questionnaire.
class QuestionnaireView(TemplateView):
    template_name = 'surveys/questions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs['slug']
        survey = get_object_or_404(Survey, slug=slug)
        context['survey'] = survey
        context['questions'] = SurveyQuestion.objects.filter(
            survey=survey).order_by('sort_index')
        context['next_page'] = reverse('surveys:response_1', args=[slug])

        # Hack, hard code for today.
        context["is_static"] = True
        context['social'] = {}
        context['social']['og_title'] = "Élections présidentielles de printemps 2022"
        context['social']['og_description'] = "Les Mobilitains interrogent les candidats aux présidentielles sur leurs projets de soutien pour de la mobilité régionale"
        context['social']['og_image'] = "asso_tn/drapeau.jpg"
        context['social']['twitter_title'] = "Élections présidentielles de printemps 2022"
        context['social']['twitter_description'] = "Les Mobilitains interrogent les candidats aux présidentielles sur leurs projets de soutien pour de la mobilité régionale"
        context['social']['twitter_image'] = "asso_tn/drapeau.jpg"

        return context

#### Views for answering questions ####################################

#### Decorate for login. ####
class ResponseView(TemplateView):
    template_name = 'surveys/response_1.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs['slug']
        survey = get_object_or_404(Survey, slug=slug)
        context['survey'] = survey
        context['questions'] = SurveyQuestion.objects.filter(
            survey=survey).order_by('sort_index')

        # Hack, hard code for today.
        context["is_static"] = True
        context['social'] = {}
        context['social']['og_title'] = "Élections présidentielles de printemps 2022"
        context['social']['og_description'] = "Les Mobilitains interrogent les candidats aux présidentielles sur leurs projets de soutien pour de la mobilité régionale"
        context['social']['og_image'] = "asso_tn/drapeau.jpg"
        context['social']['twitter_title'] = "Élections présidentielles de printemps 2022"
        context['social']['twitter_description'] = "Les Mobilitains interrogent les candidats aux présidentielles sur leurs projets de soutien pour de la mobilité régionale"
        context['social']['twitter_image'] = "asso_tn/drapeau.jpg"

        return context

#### Views for viewing results ########################################

social = {'twitter_title': "Élections régionales et départementales 2021",
          'twitter_descr': "Vos déplacements vous sont importants.  Nous agissons.",
          'twitter_image': 'asso_tn/trolley-sunset-1500w.jpg',

          'og_title': "Élections régionales et départementales 2021",
          'og_description': "Vos déplacements vous sont importants.  Nous agissons.",
          'og_image': 'asso_tn/trolley-sunset-1500w.jpg',
          }

class CommuneChooserSurveyView(TemplateView):
    template_name = 'surveys/survey.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        responders = SurveyResponder.objects.filter(
            survey_id=kwargs['survey_id'])
        context['communes'] = set([responder.commune for responder in responders])
        context['listes'] = None;
        context['questions'] = None;
        context['social'] = social
        return context

class ListeChooserSurveyView(CommuneChooserSurveyView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['this_commune'] = SurveyCommune.objects.filter(
            id=kwargs['commune_id'])[0]
        responders = SurveyResponder.objects.filter(
            survey_id=kwargs['survey_id'], commune=kwargs['commune_id'])
        context['listes'] = responders
        context['social'] = social
        return context

class QuestionChooserSurveyView(ListeChooserSurveyView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['this_liste'] = SurveyResponder.objects.filter(
            survey_id=kwargs['survey_id'],
            commune=kwargs['commune_id'],
            id=kwargs['responder_id'])[0]
        context['questions'] = SurveyQuestion.objects.filter(
            survey=kwargs['survey_id']).order_by('sort_index')
        if 'question_id' in kwargs:
            this_question = SurveyQuestion.objects.filter(
                id=kwargs['question_id'])[0]
            this_question.text_paragraphs = \
                this_question.question_text.split('\n')
            context['this_question'] = this_question
        context['social'] = social
        return context

class ResponseDisplaySurveyView(QuestionChooserSurveyView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        this_response_as_list = SurveyResponse.objects.filter(
            survey=kwargs['survey_id'],
            survey_question=kwargs['question_id'],
            survey_responder=kwargs['responder_id'])
        if this_response_as_list:
            this_response = this_response_as_list[0]
        else:
            this_response = SurveyResponse()
            this_response.survey_question = context['this_question']
            this_response.survey_responder = context['this_liste']
            this_response.survey_question_response = "La liste n'a pas répondu à cette question."
        context['this_response'] = this_response
        context['social'] = social
        return context

class QuestionnaireForSurveyView(TemplateView):
    template_name = 'surveys/questionnaire.html'
