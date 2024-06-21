from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic.base import TemplateView

from .models import (
    Survey,
    SurveyCommune,
    SurveyQuestion,
    SurveyResponder,
    SurveyResponse,
)

# This currently does nothing useful, just says it doesn't know.
# It should show a list of active questionnaires.

# Note that there is general confusion between liste and responder.  I
# should go through these views and the survey.html template and make
# them all say this_responder instead.


def hack_augment_social(context, candidate_name=""):
    """Augment context with social media data.

    This should be dynamic, but it's not.  Next election, if we still
    do this.

    """
    if candidate_name:
        title = f"{candidate_name} : pouvoir d’achat et sécurité en mobilité"
    else:
        title = "Pouvoir d’achat et sécurité en mobilité"
    description = (
        "Les déplacements compte parmi les points budgétaires les"
        " plus importants pour les français, avec le logement et la nourriture."
        "  Comment répondent les candidats ?"
    )
    image = "surveys/delacroix-mobilite-2024-wide-1_banner.jpg"
    social = {
        "twitter_title": title,
        "twitter_descr": description,
        "twitter_image": image,
        "og_title": title,
        "og_description": description,
        "og_image": image,
    }
    context["social"] = social
    context["is_static"] = True


class MainSurveyView(TemplateView):
    template_name = "surveys/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


# Show the questionns for one questionnaire.
class QuestionnaireView(TemplateView):
    template_name = "surveys/questions.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs["slug"]
        survey = get_object_or_404(Survey, slug=slug)
        context["survey"] = survey
        context["questions"] = SurveyQuestion.objects.filter(
            survey=survey
        ).order_by("sort_index")
        context["next_page"] = reverse("surveys:response_1", args=[slug])
        hack_augment_social(context)
        return context


# Views for answering questions ####################################


# Decorate for login. ####
class ResponseView(TemplateView):
    template_name = "surveys/response_1.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs["slug"]
        survey = get_object_or_404(Survey, slug=slug)
        context["survey"] = survey
        context["questions"] = SurveyQuestion.objects.filter(
            survey=survey
        ).order_by("sort_index")
        hack_augment_social(context)
        return context


# Views for viewing results ########################################


class CommuneChooserSurveyView(TemplateView):
    template_name = "surveys/survey.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        survey_identifier = kwargs["survey_identifier"]
        survey = Survey.objects.get(identifier=survey_identifier)
        responders = SurveyResponder.objects.filter(
            survey__identifier=survey_identifier
        )
        context["survey"] = survey
        context["communes"] = set(
            [responder.commune for responder in responders]
        )
        context["listes"] = None
        context["questions"] = None
        hack_augment_social(context)
        return context


class ListeChooserSurveyView(TemplateView):
    template_name = "surveys/survey.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        commune_identifier = kwargs["commune_identifier"]
        this_commune = SurveyCommune.objects.get(identifier=commune_identifier)
        responders = SurveyResponder.objects.filter(commune=this_commune)
        context["survey"] = this_commune.survey
        context["this_commune"] = this_commune
        context["communes"] = set(
            [responder.commune for responder in responders]
        )
        context["listes"] = responders
        hack_augment_social(context)
        return context


class QuestionChooserSurveyView(TemplateView):
    template_name = "surveys/survey.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        responder_identifier = kwargs["responder_identifier"]
        this_liste = SurveyResponder.objects.get(
            identifier=responder_identifier
        )
        this_commune = this_liste.commune
        this_survey = Survey.objects.get(
            identifier=this_liste.survey.identifier
        )
        questions = SurveyQuestion.objects.filter(survey=this_survey).order_by(
            "sort_index"
        )
        responders = SurveyResponder.objects.filter(commune=this_commune)

        context["survey"] = this_survey
        context["communes"] = set(
            [responder.commune for responder in responders]
        )
        context["listes"] = responders
        context["this_liste"] = this_liste
        context["questions"] = questions
        # # Once upon a time, I could hold onto questions if the only
        # # change were the responder.  I dropped that with the change
        # # to identifier codes.  I'll leave this here to remind me in
        # # case I reactivate this code in a more planned way later.
        #
        # if "question_id" in kwargs:
        #     this_question = SurveyQuestion.objects.filter(
        #         id=kwargs["question_id"]
        #     )[0]
        #     this_question.text_paragraphs = this_question.question_text.split(
        #         "\n"
        #     )
        #     context["this_question"] = this_question
        hack_augment_social(context)
        return context


class ResponseDisplaySurveyView(TemplateView):
    template_name = "surveys/survey.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        responder_identifier = kwargs["responder_identifier"]
        question_identifier = kwargs["question_identifier"]
        # There may be no response to this question, so make sure we
        # have the responder object from which we can extract the
        # commune, the survey, and so forth.
        this_responder = SurveyResponder.objects.get(
            identifier=responder_identifier
        )
        this_question = SurveyQuestion.objects.get(
            identifier=question_identifier
        )
        this_commune = this_responder.commune
        try:
            this_response = SurveyResponse.objects.get(
                survey_responder__identifier=responder_identifier,
                survey_question__identifier=question_identifier,
            )
        except SurveyResponse.DoesNotExist:
            this_response = SurveyResponse()
            this_response.survey_question = context["this_question"]
            this_response.survey_responder = context["this_liste"]
            this_response.survey_question_response = (
                "La liste n'a pas répondu à cette question."
            )
        responders = SurveyResponder.objects.filter(commune=this_commune)
        this_survey = this_responder.survey
        questions = SurveyQuestion.objects.filter(survey=this_survey).order_by(
            "sort_index"
        )
        this_liste = this_responder  # Confusing naming.

        context["survey"] = this_survey
        context["this_commune"] = this_commune
        context["communes"] = set(
            [responder.commune for responder in responders]
        )
        context["listes"] = responders
        context["this_liste"] = this_liste
        context["this_question"] = this_question
        context["questions"] = questions
        context["this_response"] = this_response
        hack_augment_social(context, this_responder.tete_de_liste)
        return context


class QuestionnaireForSurveyView(TemplateView):
    template_name = "surveys/questionnaire.html"
