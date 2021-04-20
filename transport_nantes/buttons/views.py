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
        "D": 0,
        }


    def get(self, request):

        text = request.GET.get('button_text')
        if text is not None and request.is_ajax():
            timestamp = datetime.now()
            print("\n", f"I've seen {text} at {timestamp}", "\n")
            self.letter_dict[text] += 1
            print(self.letter_dict)
            context = {
                "A_value": self.letter_dict["A"],
                "B_value": self.letter_dict["B"],
                "C_value": self.letter_dict["C"],
                "D_value": self.letter_dict["D"],
            }
            
            return JsonResponse(context, status=200)
        ButtonsView.letter_dict = {
                                "A": 0,
                                "B": 0, 
                                "C": 0,
                                "D": 0,
                                }
        return render(request, "buttons.html")
