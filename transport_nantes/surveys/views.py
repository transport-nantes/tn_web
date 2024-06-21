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
        responders = SurveyResponder.objects.filter(
            survey_id=kwargs["survey_id"]
        )
        context["communes"] = set(
            [responder.commune for responder in responders]
        )
        context["listes"] = None
        context["questions"] = None
        hack_augment_social(context)
        return context


class ListeChooserSurveyView(CommuneChooserSurveyView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["this_commune"] = SurveyCommune.objects.filter(
            id=kwargs["commune_id"]
        )[0]
        responders = SurveyResponder.objects.filter(
            survey_id=kwargs["survey_id"], commune=kwargs["commune_id"]
        )
        context["listes"] = responders
        hack_augment_social(context)
        return context


class QuestionChooserSurveyView(ListeChooserSurveyView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["this_liste"] = SurveyResponder.objects.filter(
            survey_id=kwargs["survey_id"],
            commune=kwargs["commune_id"],
            id=kwargs["responder_id"],
        )[0]
        context["questions"] = SurveyQuestion.objects.filter(
            survey=kwargs["survey_id"]
        ).order_by("sort_index")
        if "question_id" in kwargs:
            this_question = SurveyQuestion.objects.filter(
                id=kwargs["question_id"]
            )[0]
            this_question.text_paragraphs = this_question.question_text.split(
                "\n"
            )
            context["this_question"] = this_question
        hack_augment_social(context)
        return context


class ResponseDisplaySurveyView(QuestionChooserSurveyView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        survey_responder_id = kwargs["responder_id"]
        survey_responder = SurveyResponder.objects.get(id=survey_responder_id)
        this_response_as_list = SurveyResponse.objects.filter(
            survey=kwargs["survey_id"],
            survey_question=kwargs["question_id"],
            survey_responder=survey_responder_id,
        )
        if this_response_as_list:
            this_response = this_response_as_list[0]
        else:
            this_response = SurveyResponse()
            this_response.survey_question = context["this_question"]
            this_response.survey_responder = context["this_liste"]
            this_response.survey_question_response = (
                "La liste n'a pas répondu à cette question."
            )
        context["this_response"] = this_response
        hack_augment_social(context, survey_responder.tete_de_liste)
        return context


class QuestionnaireForSurveyView(TemplateView):
    template_name = "surveys/questionnaire.html"
