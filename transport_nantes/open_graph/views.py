# from django.shortcuts import render
from django.http import HttpResponse
from PIL import Image,ImageDraw,ImageFont

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
