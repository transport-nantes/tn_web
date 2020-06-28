# from django.shortcuts import render
from django.http import HttpResponse
from PIL import Image,ImageDraw,ImageFont
import datetime

# Create your views here.

"""
Some scratch stuff:

img = Image.open('transport_nantes/open_graph/base_images/parlons-mobilite.png')
img.show()
draw = ImageDraw.Draw(img)
ImageFont.truetype('transport_nantes/open_graph/base_images/Montserrat/MontserratAlternates-Bold.otf')
text_width, text_height = font.getsize('hello, world')
draw.text((140, 70), "Vélopolitain", font=font, fill=(0,0,0))


"""
TN_logo_blue = (90, 194, 231)     # 5AC2E7
TN_logo_orange = (250, 71, 18)    # FA4712
TN_logo_red = (127, 105, 102)     # 7F6966
TN_logo_green = (68, 83, 109)     # 44536D

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
    #### This will only work in dev due to path name.
    image = Image.open('open_graph/base_images/parlons-mobilite.png')
    
    response = HttpResponse(content_type='image/png')
    image.save(response, image.format)
    return response

def generate_100_days_image(request, day_offset, edile=''):
    """Create an image for the first 100 days project.

    """
    if (day_offset < 0):
        J_days = 'J{d}'.format(d=day_offset)
    else:
        J_days = 'J+{d}'.format(d=day_offset)
    #### This will only work in dev due to path name.
    image = Image.open('open_graph/base_images/100jours.png')
    draw = ImageDraw.Draw(image)
    #### This will only work in dev due to path name.
    font_path = 'open_graph/base_images/Montserrat/MontserratAlternates-Bold.otf'
    font_size_name = 50
    font_size_day = 150
    font_name = ImageFont.truetype(font_path, font_size_name)
    font_day = ImageFont.truetype(font_path, font_size_day)
    #draw.text((290, 110), J_days, font=font_day, fill=tuple([int(.5 * x) for x in TN_logo_blue]))
    draw.text((290, 110), J_days, font=font_day, fill=TN_logo_red)
    draw.text((120, 120), edile, font=font_name, fill=TN_logo_blue)
    response = HttpResponse(content_type='image/png')
    image.save(response, image.format)
    return response
