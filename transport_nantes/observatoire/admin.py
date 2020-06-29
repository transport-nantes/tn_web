from django.contrib import admin

from .models import Observatoire, ObservatoirePerson, \
    ObservatoireObjective, ObservatoireProgress

# Register your models here.
admin.site.register(Observatoire)
admin.site.register(ObservatoirePerson)
admin.site.register(ObservatoireObjective)
admin.site.register(ObservatoireProgress)
