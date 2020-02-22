from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Survey

def index(request):
    return HttpResponse("Hello, world!  I'm going to be a survey.  This page isn't valid.")

def choose_commune(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    return render(request, 'surveys/index.html', {})
#"This page is for selecting a commune.")

def choose_liste(request, survey_id, commune_id):
    return HttpResponse("This page is for selecting a list.")

def choose_question(request, survey_id, commune_id, liste_id):
    return HttpResponse("This page is for selecting a question.")

def choose_response(request, survey_id, commune_id, liste_id, question_id):
    return HttpResponse("This page is for displaying a response.")

