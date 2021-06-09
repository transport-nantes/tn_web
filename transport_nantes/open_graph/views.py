# from django.shortcuts import render
from django.http import HttpResponse
from PIL import Image,ImageDraw,ImageFont
import datetime
from surveys.models import SurveyCommune, SurveyResponder, SurveyQuestion

"""
Some scratch stuff:

img = Image.open('transport_nantes/open_graph/base_images/parlons-mobilite.png')
img.show()
draw = ImageDraw.Draw(img)
ImageFont.truetype('transport_nantes/open_graph/base_images/Montserrat/MontserratAlternates-Bold.otf')
text_width, text_height = font.getsize('hello, world')
draw.text((140, 70), "Vélopolitain", font=font, fill=(0,0,0))


"""
TN_logo_gray = (221, 229, 237)    # DDE5ED
TN_logo_red = (127, 105, 102)     # 7F6966
TN_logo_blue = (91, 194, 231)     # 5BC2E7
TN_logo_orange = (250, 70, 23)    # FA4616
TN_logo_dark_blue = (51, 63, 72)  # 333F48
#
TN_logo_green = (68, 83, 109)     # 44536D -- ?

def generate_questionnaire_image(request):
    """Create an image for a questionnaire response page.

    In real life (i.e., in further commits) this must take arguments
    so that it knows what to display.  This will assuredly require
    model changes in the survey app so that we can know the text to
    display here.

    The intent is that open graph images are fetched once on URL
    share, so it's not too expensive just to render them each time
    we're asked.  Indeed, the URL's should have a random nonce
    attached so that they get refetched (so that we can update them on
    reshare).

    """
    image = Image.open('open_graph/base_images/parlons-mobilite.png')
    
    response = HttpResponse(content_type='image/png')
    image.save(response, image.format)
    return response

def survey_base_image_with_commune(commune):
    """Create and return an image for the requested commune.

    This is the base function.  We'll annotate it further with
    candidate name or question as needed.
    """
    image = Image.open('surveys/base_images/2021-election.jpg')
    draw = ImageDraw.Draw(image)
    font_path = 'open_graph/base_images/Montserrat/Montserrat-Bold.otf'
    def font_size(str_length):
        short_str_length = 10
        short_font_size = 140
        long_str_length = 35
        long_font_size = 70
        return (str_length - short_str_length) * long_font_size / \
            (long_str_length - short_str_length)                  \
            + (str_length-long_str_length) * short_font_size /    \
            (short_str_length-long_str_length)

    name_string = "{commune}".format(commune=commune.commune)
    font_size_name = int(font_size(len(name_string)))
    font_name = ImageFont.truetype(font_path, font_size_name)
    draw.text((120, 120), name_string, font=font_name, fill=TN_logo_gray)
    return image

def survey_image_with_candidate(candidate):
    """Create and return an image for the requested candidate.

    """
    image = survey_base_image_with_commune(candidate.commune)
    draw = ImageDraw.Draw(image)
    font_path = 'open_graph/base_images/Montserrat/Montserrat-Bold.otf'
    def font_size(str_length):
        short_str_length = 10
        short_font_size = 120
        long_str_length = 30
        long_font_size = 60
        return (str_length - short_str_length) * long_font_size / \
            (long_str_length - short_str_length)                  \
            + (str_length-long_str_length) * short_font_size /    \
            (short_str_length-long_str_length)

    name_string = "{candidate}".format(candidate=candidate.tete_de_liste)
    font_size_name = int(font_size(len(name_string)))
    font_name = ImageFont.truetype(font_path, font_size_name)
    draw.text((160, 300), name_string, font=font_name, fill=TN_logo_gray)
    return image

def survey_image_with_question(candidate, question):
    """Create and return an image for the requested survey response.

    """
    image = survey_image_with_candidate(candidate)
    draw = ImageDraw.Draw(image)
    font_path = 'open_graph/base_images/Montserrat/Montserrat-Bold.otf'
    def font_size(str_length):
        short_str_length = 10
        short_font_size = 120
        long_str_length = 35
        long_font_size = 60
        return (str_length - short_str_length) * long_font_size / \
            (long_str_length - short_str_length)                  \
            + (str_length-long_str_length) * short_font_size /    \
            (short_str_length-long_str_length)

    name_string = "{question}".format(question=question.question_title)
    font_size_name = int(font_size(len(name_string)))
    font_name = ImageFont.truetype(font_path, font_size_name)
    draw.text((120, 500), name_string, font=font_name, fill=TN_logo_dark_blue)
    return image

def generate_election_commune_image(request, commune_id):

    """Create an image for a survey response.

    """
    commune = SurveyCommune.objects.filter(id=commune_id)[0]
    image = survey_base_image_with_commune(commune)
    response = HttpResponse(content_type='image/png')
    image.save(response, image.format)
    return response

def generate_election_candidate_image(request, candidate_id):
    """Create an image for a survey response.

    """
    candidate = SurveyResponder.objects.filter(id=candidate_id)[0]
    image = survey_image_with_candidate(candidate)
    response = HttpResponse(content_type='image/png')
    image.save(response, image.format)
    return response

def generate_election_question_image(request, candidate_id, question_id):
    """Create an image for a survey response.

    """
    candidate = SurveyResponder.objects.filter(id=candidate_id)[0]
    question = SurveyQuestion.objects.filter(id=question_id)[0]
    image = survey_image_with_question(candidate, question)
    response = HttpResponse(content_type='image/png')
    image.save(response, image.format)
    return response
