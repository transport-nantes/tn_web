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

    def test_buttons(self):
        self.assertEqual(self.parser.transform('[[don:]]((give!))'), \
                         don.bouton_don('give!'))
        self.assertEqual(self.parser.transform('[[don:large]]((give!))'), \
                         don.bouton_don_lg('give!'))
        self.assertEqual(self.parser.transform('[[don:adhésion]]((give!))'), \
                         don.bouton_join('give!'))

    def test_call_to_action(self):
        self.assertEqual(self.parser.transform('[[action:join us!]]((my_topic_name))'), \
                         don.action_button(reverse(
                             'topic_blog:view_topic',
                             args=['my_topic_name']),
                                           'join us!'))
