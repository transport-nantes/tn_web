from django import template
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from .markdown import tn_markdown
register = template.Library()


@register.simple_tag(takes_context=True)
def email_full_width_image(
        context: dict,
        filepath: str, alt_text: str,
        link: str = "https://mobilitains.fr") -> str:
    request = context['request']
    html_template = """
    <tr>
        <td
        style="padding:0;font-size:24px;line-height:28px;font-weight:bold;background-color:#ffffff;">
            <a href="{link}" style="text-decoration:none;">
                <img src="{filepath}" width="600" alt="{alt_text}"
                style="width:70%;margin:auto;height:auto;display:block;border:none;text-decoration:none;color:#363636;padding-bottom:15px;">
            </a>
        </td>
    </tr>
    """.format(
        filepath=request.build_absolute_uri(filepath),
        alt_text=alt_text,
        link=link)
    return mark_safe(html_template)


@register.simple_tag(takes_context=True)
def email_body_text_md(context, text: str) -> str:
    html_template = """
    <tr>
        <td style="padding:30px;background-color:#ffffff;">
            <p style="margin:0;">
                {text}
            </p>
        </td>
    </tr>
    """.format(text=tn_markdown(context, text))
    return mark_safe(html_template)


@register.simple_tag(takes_context=True)
def email_cta_button(context: dict, slug: str, label: str) -> str:
    tbe_path = reverse_lazy(
        "topicblog:view_item_by_slug",
        kwargs={"the_slug": slug}
    )
    host = context["request"].get_host()
    scheme = context["request"].scheme
    html_template = """
    <tr>
        <td style="padding-right:30px;padding-left:30px;padding-bottom:15px;
        background-color:#ffffff;text-align:center;">
            <p>
                <a href="{scheme}://{host}{tbe_path}" class="btn donation-button btn-lg" 
                style="background-color: #5BC2E7;color:white;font-weight: 600;">
                    {label} <i class="fa fa-arrow-right" area-hidden="true"></i>
                </a>
            </p>
        </td>
    </tr>
    """.format(
        scheme=scheme,
        host=host,
        tbe_path=tbe_path,
        label=label)
    return mark_safe(html_template)
