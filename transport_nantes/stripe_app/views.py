from django.views.generic.base import TemplateView, View
from django.http import JsonResponse

import stripe

# test key, will be in a separated file on prod
stripe.api_key = 'sk_test_JA5eW82rv6lp61vNAwRUFIrr00rhzXUsLW'

# Create your views here.
class StripeView(TemplateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.template_name = "stripe_app/checkout.html"

        return context

    # def create_checkout_session(self, request, *args, **kwargs):

    #     checkout_session = stripe.checkout.Session.create(

    #         payment_method_types=['card'],

    #         line_items=[

    #             {
    #                 'price_data': {
    #                     'currency': 'eur',
    #                     'unit_amount': 20,
    #                     'product_data': {
    #                         'name': 'Soutien à Mobilitains',
    #                         'images': ['https://i.imgur.com/EHyR2nP.png'],
    #                     },
    #                 },
    #                 'quantity': 1,
    #             },
    #         ],

    #         mode='payment',

    #         success_url= request.get_host() + '/success.html',

    #         cancel_url= request.get_host() + '/cancel.html',

    #     )

    #     return JsonResponse({'id': checkout_session.id})

class CheckoutSession(View):

    def get(self, **kwargs):
        checkout_session = stripe.checkout.Session.create(

            payment_method_types=['card'],

            line_items=[

                {
                    'price_data': {
                        'currency': 'eur',
                        'unit_amount': 20,
                        'product_data': {
                            'name': 'Soutien à Mobilitains',
                            'images': ['https://i.imgur.com/EHyR2nP.png'],
                        },
                    },
                    'quantity': 1,
                },
            ],

            mode='payment',

            success_url= self.request.get_host() + '/success.html',

            cancel_url= self.request.get_host() + '/cancel.html',

        )

        return JsonResponse({'id': checkout_session.id})
