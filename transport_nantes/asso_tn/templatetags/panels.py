from django import template

register = template.Library()

@register.inclusion_tag('asso_tn/projects.html')
def show_projects(but_not=None):
    """Render our four principle projects at this point.

    If but_not is not None, it is a project not to render.

    Eventually this should be database-driven.  For now, it is static.

    """
    return {}
