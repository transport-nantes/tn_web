from django.template import Library, Template, Context
from django.utils.safestring import mark_safe

register = Library()


@register.simple_tag(takes_context=True)
def socials_share_buttons(context: dict):
    html_template = """
    <div id="share-buttons" class="d-flex flex-row col-12 mb-2 justify-content-center">
        <i class="fa-solid fa-share-nodes pt-1 mr-5" style="font-size:40px;color:var(--body-text)"></i>
        <a href="https://twitter.com/intent/tweet?url={{ request.build_absolute_uri|urlencode}}"
        target="_blank"
        class="d-flex border-circle p-2 mr-2 font-xl border-blue-light bg-blue-light"
        style="width:fit-content;color:white;">
            <i class="fab fa-twitter mx-auto"></i>
        </a>
        <a href="http://www.facebook.com/share.php?u={{ request.build_absolute_uri|urlencode }}"
        target="_blank"
        class="d-flex border-circle p-2 font-xl border-blue-light bg-blue-light"
        style="width:fit-content;color:white;">
            <i class="fab fa-facebook"></i>
        </a>
    </div>
    """  # noqa
    return mark_safe(Template(html_template).render(Context(context)))
