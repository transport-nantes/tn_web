from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, world!  I'm going to be a survey.  This page isn't valid.")

def choose_commune(request, survey_id):
    return HttpResponse("This page is for selecting a commune.")

def choose_liste(request, survey_id, commune_id):
    return HttpResponse("This page is for selecting a list.")

def choose_question(request, survey_id, commune_id, liste_id):
    return HttpResponse("This page is for selecting a question.")

def choose_response(request, survey_id, commune_id, liste_id, question_id):
    return HttpResponse("This page is for displaying a response.")

