from django.shortcuts import render
from django.views.generic.base import View
from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime

# Create your views here.
class ButtonsView(View):

    letter_dict = {
        "A": 0,
        "B": 0, 
        "C": 0,
        "D":0,
        }

    def get(self, request):
        text = request.GET.get('button_text')
        if text is not None:
            timestamp = datetime.now()
            print("\n", f"I've seen {text} at {timestamp}", "\n")
            self.letter_dict[text] += 1
            print(self.letter_dict)

        return render(request, "buttons.html")
