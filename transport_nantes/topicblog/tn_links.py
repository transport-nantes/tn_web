from django.conf import settings
from django.template import Template, Context
from django.urls import reverse, NoReverseMatch

from asso_tn.templatetags import don
from mailing_list.templatetags import newsletter

"""Filter for Transport Nantes specific non-standard markdown.

Provide a filter that parses text and renders certain non-standard
markdown transformations that we use.  In particular, we use this to
provide various donation buttons and calls to action.

A good syntax summary for markdown lives here:

    https://www.markdownguide.org/basic-syntax

We extend markdown somewhat here in order to provide better
integration with our own software.  The intent
(cf. topicblog/templatetags/markdown.py) is that we escape user text,
apply our transformer, then markdown, then mark as safe.  Note that
generic markdown accepts HTML, but we don't want to accept HTML from
users for security.  Running our transformations before markdown just
avoids having to consider the effect of our notation on markdown (in
principle, none, but easiest just avoided).  It also lets us assume
that no HTML is present in our input.

The format of the notation we interpret is this:

    [[class:label]]((satellite))

The label is optional but the ':' is not.

Some examples:

    [[don:]]((text))           equivalent to {% bouton_don "text" %}
    [[don:large]]((text))      equivalent to {% bouton_don_lg "text" %}
    [[don:adhésion]]((text))   equivalent to {% bouton_join "text" %}

    [[news:name]]((text))      equivalent to {% show_mailing_list %}

    [[action:text]]((topic_slug))
                               equivalent to [text](/tb/t/topic_slug/)
    [[contact:button-label]]((email-subject-label))
                               button that opens an email

    [[externe:label]]((URL))   equivalent to [text](URL) (for external links)
    [[EXTERNE:label]]((URL))   externe but a button with arrow
    [[petition:label]]((petition_slug))
                               equivalent to [text](/ml/petition/petition_slug/)

Note that we assume that there is no HTML in the incoming text and
that standard markdown transformations will applied on output.  The
results will be inserted into templates after django renders the page,
so we don't make use of template substitutions.

The HTML safety checks must have been applied before calling these
functions in order to permit HTML on the output.

"""

def render_inclusion_tag_to_html(tag_source, tag_name):
    """Render an inclusion tag to a string.
    """

    template_string = f"{{% load {tag_source} %}}{{% {tag_name} %}}"
    template_context = {'csrf_token': settings.csrf_token}
    html = Template(template_string).render(Context(template_context))
    return html

from enum import Enum, unique, auto

@unique
class State(Enum):
    ORDINARY = auto()

    PARSING_OPEN_BRACKET = auto()
    IN_DOUBLE_BRACKET_CLASS = auto()
    IN_DOUBLE_BRACKET_LABEL = auto()
    PARSING_CLOSE_BRACKET = auto()

    EXPECTING_DOUBLE_PAREN = auto()
    PARSING_OPEN_PAREN = auto()
    IN_DOUBLE_PAREN = auto()
    PARSING_CLOSE_PAREN = auto()

class TNLinkParser(object):
    """
    """

    # Accumulators.
    out_string = ''
    bracket_class_string = ''
    bracket_label_string = ''
    paren_string = ''
    # Current state.
    state = State.ORDINARY
    verbose = False

    def __init__(self, verbose=False):
        self.verbose = verbose

    def clear(self):
        """Clear state before parsing.
        """
        self.out_string = ''
        self.bracket_class_string = ''
        self.bracket_label_string = ''
        self.paren_string = ''
        self.state = State.ORDINARY

    def transform(self, in_text):
        """Parse text and return output.

        Transform incoming text as noted in the file header.

        """
        self.clear()
        self.log(in_text)
        self.consume_ordinary(in_text)
        return self.out_string

    def log(self, message):
        if self.verbose:
            print(message)

    def set_state(self, state):
        self.log(state.name)
        self.state = state

    def _flush(self):
        """Internal function: flush accumulators."""
        if State.ORDINARY == self.state:
            return
        self.out_string += '['
        if State.PARSING_OPEN_BRACKET == self.state:
            return
        self.out_string += '[' + self.bracket_class_string
        if State.IN_DOUBLE_BRACKET_CLASS == self.state:
            return
        self.out_string += ':' + self.bracket_label_string
        if State.IN_DOUBLE_BRACKET_LABEL == self.state:
            return
        self.out_string += ']'
        if State.PARSING_CLOSE_BRACKET == self.state:
            return
        self.out_string += ']'
        if State.EXPECTING_DOUBLE_PAREN == self.state:
            return
        self.out_string += '('
        if State.PARSING_OPEN_PAREN == self.state:
            return
        self.out_string += '(' + self.paren_string
        if State.IN_DOUBLE_PAREN == self.state:
            return
        self.out_string += ')'
        if State.PARSING_CLOSE_PAREN == self.state:
            return
        self.out_string += ')'

    def reset_to_ordinary(self):
        """Reset to ordinary, clear accumulators."""
        self.log('Reset')
        self.bracket_class_string = ''
        self.bracket_label_string = ''
        self.paren_string = ''
        self.state = State.ORDINARY

    def flush_and_reset_to_ordinary(self, char):
        """Flush state and go back to ORDINARY.

        We thought we were doing something useful, but the user was
        thinking otherwise, so flush state as needed and go back to
        ordinary pass-through.
        """
        self.log('Flush and reset')
        self._flush()
        self.out_string += char
        self.reset_to_ordinary()

    def transcribe_accumulated_text(self):
        """We've finished accumulating something, transform and output it.

        This is where the magic happens.
        """
        if 'don' == self.bracket_class_string:
            if '' == self.bracket_label_string:
                self.out_string += don.bouton_don(self.paren_string)
            elif 'large' == self.bracket_label_string:
                self.out_string += don.bouton_don_lg(self.paren_string)
            elif 'adhésion' == self.bracket_label_string:
                self.out_string += don.bouton_join(self.paren_string)
            else:
                self.out_string += self.bracket_class_string + ':' + \
                    self.bracket_label_string + '(' + self.paren_string + ')'
        elif 'news' == self.bracket_class_string:
            newsletter_name = self.bracket_label_string
            description_text = self.paren_string
            self.out_string += render_inclusion_tag_to_html('newsletter', 'show_mailing_list')
            # Bug: this doesn't take into account the mailing list
            # requested or the label we request.
        elif 'action' == self.bracket_class_string:
            try:
                url = reverse('topic_blog:view_topic', args=[self.paren_string])
            except NoReverseMatch:
                url = '(((pas trouvé : {ps})))'.format(ps=self.paren_string)
            self.out_string += don.action_button(url, self.bracket_label_string)
        elif 'contact' == self.bracket_class_string:
            self.out_string += don.contact_button(self.bracket_label_string, self.paren_string)
        elif 'externe' == self.bracket_class_string:
            url = self.paren_string
            self.out_string += don.external_url(url, self.bracket_label_string)
        elif 'EXTERNE' == self.bracket_class_string:
            url = self.paren_string
            self.out_string += don.external_url_button(url, self.bracket_label_string)
        elif 'petition' == self.bracket_class_string:
            self.out_string += newsletter.petition_link(self.paren_string, self.bracket_label_string)
        else:
            self.out_string += f"[[{self.bracket_class_string}:{self.bracket_label_string}]](({self.paren_string}))"
            self.log('Unexpected transcription case: ' + self.bracket_class_string)

    def consume_ordinary(self, in_text):
        """

        In brief, transform patterns like [[class:label]]((satellite))
        to the appropriate text, HTML, or markdown.

        """
        for s in in_text:
            if '[' == s:
                if State.ORDINARY == self.state:
                    self.set_state(State.PARSING_OPEN_BRACKET)
                elif State.PARSING_OPEN_BRACKET == self.state:
                    self.set_state(State.IN_DOUBLE_BRACKET_CLASS)
                else:
                    self.flush_and_reset_to_ordinary(s)
            elif ':' == s:
                if State.IN_DOUBLE_BRACKET_CLASS == self.state:
                    self.set_state(State.IN_DOUBLE_BRACKET_LABEL)
                elif State.IN_DOUBLE_PAREN == self.state:
                    # Colons are permitted between double parens.
                    self.paren_string += s
                else:
                    self.flush_and_reset_to_ordinary(s)
            elif ']' == s:
                if State.IN_DOUBLE_BRACKET_LABEL == self.state:
                    self.set_state(State.PARSING_CLOSE_BRACKET)
                elif State.PARSING_CLOSE_BRACKET == self.state:
                    self.set_state(State.EXPECTING_DOUBLE_PAREN)
                else:
                    self.flush_and_reset_to_ordinary(s)
            elif '(' == s:
                if State.EXPECTING_DOUBLE_PAREN == self.state:
                    self.set_state(State.PARSING_OPEN_PAREN)
                elif State.PARSING_OPEN_PAREN == self.state:
                    self.set_state(State.IN_DOUBLE_PAREN)
                else:
                    self.flush_and_reset_to_ordinary(s)
            elif ')' == s:
                if State.IN_DOUBLE_PAREN == self.state:
                    self.set_state(State.PARSING_CLOSE_PAREN)
                elif State.PARSING_CLOSE_PAREN == self.state:
                    self.transcribe_accumulated_text()
                    self.set_state(State.ORDINARY)
                    self.reset_to_ordinary()
                else:
                    self.flush_and_reset_to_ordinary(s)
            else:
                # Contexts in which we accumulate text.
                if State.IN_DOUBLE_BRACKET_CLASS == self.state:
                    self.bracket_class_string += s
                elif State.IN_DOUBLE_BRACKET_LABEL == self.state:
                    self.bracket_label_string += s
                elif State.IN_DOUBLE_PAREN == self.state:
                    self.paren_string += s
                elif State.ORDINARY == self.state:
                    self.out_string += s
                else:
                    self.flush_and_reset_to_ordinary(s)

        self.log('At end of consume_ordinary, flushing.')
        # At end of string, flush any remaining buffered data.
        self.flush_and_reset_to_ordinary('')
