import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView

from .forms import UsernameEditForm

logger = logging.getLogger("django")


class MainTransportNantes(TemplateView):
    template_name = "asso_tn/index.html"
    twitter_image = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hero"] = True
        context[
            "hero_image"
        ] = "asso_tn/images-quentin-boulegon/pont-rousseau-1.jpg"
        context[
            "hero_title"
        ] = "Pour une mobilité sûre, vertueuse, et agréable"
        context["title"] = "Mobilitains - Pour une mobilité multimodale"
        context["twitter_image"] = "asso_tn/accueil-mobilité-multimodale.jpg"
        return context


class AssoView(TemplateView):
    title = None
    hero_image = None
    hero_title = None
    hero_description = None
    meta_descr = ""
    twitter_title = ""
    twitter_descr = ""
    twitter_image = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        social = {}
        social["twitter_title"] = self.twitter_title
        social["twitter_description"] = self.twitter_descr
        social["twitter_image"] = self.hero_image
        social["og_image"] = self.hero_image
        page = {}
        page["meta_descr"] = self.meta_descr
        context["title"] = self.title
        context["page"] = page
        context["social"] = social
        if self.hero_image is not None:
            context["hero"] = True
            context["hero_image"] = self.hero_image
            context["hero_title"] = self.hero_title or ""
            context["hero_description"] = self.hero_description or ""
            context["is_static"] = True
        return context


def tn_404_view(request, exception):
    """TN custom 404 view."""
    return render(request, "asso_tn/404.html", status=404)


class PreferencesView(LoginRequiredMixin, TemplateView):
    """Display one's preferences."""

    template_name = "asso_tn/preferences.html"


class EditUsernameView(LoginRequiredMixin, UpdateView):
    """Edit one's username."""

    # Criteria to filter the user to edit
    slug_url_kwarg = "username"
    slug_field = "username"
    model = User
    form_class = UsernameEditForm

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(["POST"])

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.check_object_permissions()
        return super().post(request, *args, **kwargs)

    def check_object_permissions(self):
        """Check that the user is allowed to change this User."""
        if all(
            [
                self.request.user != self.object,
                not self.request.user.has_perm("auth.change_user"),
            ]
        ):
            logger.warning(
                f"{self.request.user} tried to edit username of user "
                f"{self.object.username} but is not allowed to do so"
            )
            raise PermissionDenied()

    def form_valid(self, *args, **kwargs):
        """Log the username edit."""
        logger.info(f"{self.request.user} edited their username.")
        self.success_url = reverse("asso_tn:preferences")
        return super().form_valid(*args, **kwargs)

    def form_invalid(self, form):
        """Add message to warn the user that the username is not available."""
        messages.warning(
            self.request, "Ce nom d'utilisateur n'est pas disponible."
        )
        return redirect("asso_tn:preferences")
