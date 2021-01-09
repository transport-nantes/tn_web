# from django.test import TestCase
from django.urls import reverse
from unittest import TestCase

from asso_tn.templatetags import don
from .tn_links import TNLinkParser

class TnLinkParserTest(TestCase):
    def setUp(self):
        self.parser = TNLinkParser(verbose=False)

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
                         don.action_button(reverse('topic_blog:view_topic',
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

    def test_call_to_action(self):
        self.assertEqual(self.parser.transform('[[action:join us!]]((my_topic_name))'), \
                         don.action_button(reverse(
                             'topic_blog:view_topic',
                             args=['my_topic_name']),
                                           'join us!'))

    def test_two_buttons(self):
        button1 = '[[action:join us!]]((my_topic_name))'
        html1 = don.action_button(reverse('topic_blog:view_topic',
                                          args=['my_topic_name']),
                                  'join us!')
        button2 = '[[don:adhésion]]((give!))'
        html2 = don.bouton_join('give!')
        one = self.parser.transform(button1 + button2)
        self.assertEqual(self.parser.transform(button1 + button2), \
                         html1 + html2)
