from django import template

register = template.Library()

@register.inclusion_tag('asso_tn/panel_projects.html')
def show_projects(but_not=None):
    """Render our four principle projects at this point.

    If but_not is not None, it is a project not to render.

    Eventually this should be database-driven.  For now, it is static.

    """
    return {}

@register.inclusion_tag('asso_tn/panel_volunteer.html')
def show_volunteer():
    """Render a proposal to volunteer.

    """
    return {}

@register.inclusion_tag('asso_tn/panel_donate.html')
def show_donate():
    """Render a proposal to donate.

    """
    return {}

@register.inclusion_tag('asso_tn/panel_qui_sommes_nous.html')
def show_qui_sommes_nous():
    """Render a brief history.

    """
    return {}
