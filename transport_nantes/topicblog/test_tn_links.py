# from django.test import TestCase
from django.conf import settings
from django.urls import reverse
from unittest import TestCase

from asso_tn.templatetags import don
from mailing_list.templatetags import newsletter
from .templatetags import slug
from .tn_links import TNLinkParser, render_inclusion_tag_to_html

class TnLinkParserTest(TestCase):
    def setUp(self):
        self.parser = TNLinkParser({}, verbose=False)

    def test_broken_links(self):
        self.assertEqual(self.parser.transform('[['), '[[')
        self.assertEqual(self.parser.transform(']]'), ']]')
        self.assertEqual(self.parser.transform('(('), '((')
        self.assertEqual(self.parser.transform('))'), '))')
        self.assertEqual(self.parser.transform('[dog]'), '[dog]')
        self.assertEqual(self.parser.transform('[dog]('), '[dog](')
        self.assertEqual(self.parser.transform('[dog](('), '[dog]((')
        self.assertEqual(self.parser.transform('[dog](hat)'), '[dog](hat)')
        self.assertEqual(self.parser.transform('[dog]((hat))'), '[dog]((hat))')
        self.assertEqual(self.parser.transform('[dog:cat]'), '[dog:cat]')
        self.assertEqual(self.parser.transform('[[hello'), '[[hello')
        self.assertEqual(self.parser.transform('[[hello]]((goodbye))'), '[[hello]]((goodbye))')
        self.assertEqual(self.parser.transform('[[hello:goodbye'), '[[hello:goodbye')
        self.assertEqual(self.parser.transform('[[hello:goodbye]'), '[[hello:goodbye]')
        self.assertEqual(self.parser.transform('dog [[hello:goodbye]] cat'),
                         'dog [[hello:goodbye]] cat')

    def test_bad_url(self):
        self.assertEqual(self.parser.transform(
            '[[action:Do something!]]((does-not-exist))'),
                         don.action_button(reverse('topic_blog:view_item_by_slug',
                                                   args=['does-not-exist']),
                                           'Do something!'))

    def test_buttons(self):
        self.assertEqual(self.parser.transform('[[don:]]((give!))'), \
                         don.bouton_don('give!'))
        self.assertEqual(self.parser.transform('[[don:large]]((give!))'), \
                         don.bouton_don_lg('give!'))
        self.assertEqual(self.parser.transform('[[don:adhésion]]((give!))'), \
                         don.bouton_join('give!'))
        self.assertEqual(self.parser.transform(
            '[[contact:Hello, World!]]((Je veux être bénévole))'), \
                         don.contact_button('Hello, World!', 'Je veux être bénévole'))
        self.assertEqual(self.parser.transform('[[don:fixed|1]]((give!))'), \
                         don.fixed_amount_donation_button(1, 'give!'))
        self.assertEqual(self.parser.transform('[[don:fixed|5]]((give!))'), \
                         don.fixed_amount_donation_button(5, 'give!'))

    ## Disabled due to captcha matching.
    ## Think of better way to test [[news:*]]((...)).
    #def test_news(self):
    #    settings.csrf_token = 'some text that must exist'
    #    self.assertEqual(self.parser.transform('[[news:kangaroo]]((aardvark))'), \
    #                     render_inclusion_tag_to_html('newsletter',              \
    #                                                  'show_mailing_list',       \
    #                                                  {'mailinglist': 'kangaroo'}))

    def test_external_url(self):
        url = 'my-url'
        label = 'my-label-text'
        markdown = '[[externe:{label}]](({url}))'.format(label=label, url=url)
        html = don.external_url(url, label)
        self.assertEqual(self.parser.transform(markdown), html)

        markdown = 'dog [[externe:{label}]](({url})) cat'.format(label=label, url=url)
        html = 'dog ' + don.external_url(url, label) + ' cat'
        self.assertEqual(self.parser.transform(markdown), html)

        self.parser = TNLinkParser({}, verbose=False)
        pdll = 'Pays de la Loire'
        pdll_url = 'https://dog/cat/horse'
        markdown = '[[externe:{label}]](({url}))'.format(label=pdll, url=pdll_url)
        html = don.external_url(pdll_url, pdll)
        self.assertEqual(self.parser.transform(markdown), html)

    def test_external_url_button(self):
        url = 'my-url'
        label = 'my-label-text'
        markdown = '[[EXTERNE:{label}]](({url}))'.format(label=label, url=url)
        html = don.external_url_button(url, label)
        self.assertEqual(self.parser.transform(markdown), html)

        markdown = 'dog [[EXTERNE:{label}]](({url})) cat'.format(label=label, url=url)
        html = 'dog ' + don.external_url_button(url, label) + ' cat'
        self.assertEqual(self.parser.transform(markdown), html)

        self.parser = TNLinkParser({}, verbose=False)
        pdll = 'Pays de la Loire'
        pdll_url = 'https://dog/cat/horse'
        markdown = '[[EXTERNE:{label}]](({url}))'.format(label=pdll, url=pdll_url)
        html = don.external_url_button(pdll_url, pdll)
        self.assertEqual(self.parser.transform(markdown), html)

    def test_internal_url(self):
        the_slug = 'my-slug'
        the_label = 'my-label-text'
        markdown = f'[[slug:{the_label}]](({the_slug}))'
        html = slug.tbi_slug(the_label, the_slug)
        self.assertEqual(self.parser.transform(markdown), html)

    def test_petition_url(self):
        label = 'my-label-text'
        petition = 'my-petition'
        markdown = '[[petition:{label}]](({petition}))'.format(
            label=label, petition=petition)
        html = newsletter.petition_link(petition, label)
        self.assertEqual(self.parser.transform(markdown), html)

        markdown = 'dog [[petition:{label}]](({petition})) cat'.format(
            label=label, petition=petition)
        html = 'dog ' + newsletter.petition_link(petition, label) + ' cat'
        self.assertEqual(self.parser.transform(markdown), html)

    def test_call_to_action(self):
        self.assertEqual(self.parser.transform('[[cta:join us!]]((my_topic_name))'), \
                         don.action_button(reverse(
                             'topic_blog:view_item_by_slug',
                             args=['my_topic_name']),
                                           'join us!'))
        # Deprecated version:
        self.assertEqual(self.parser.transform('[[action:join us!]]((my_topic_name))'), \
                         don.action_button(reverse(
                             'topic_blog:view_item_by_slug',
                             args=['my_topic_name']),
                                           'join us!'))

    def test_two_buttons(self):
        button1 = '[[action:join us!]]((my_topic_name))'
        html1 = don.action_button(reverse('topic_blog:view_item_by_slug',
                                          args=['my_topic_name']),
                                  'join us!')
        button2 = '[[don:adhésion]]((give!))'
        html2 = don.bouton_join('give!')
        one = self.parser.transform(button1 + button2)
        self.assertEqual(self.parser.transform(button1 + button2), \
                         html1 + html2)
