from django.test import TestCase
from .models import UTM
from django.utils.crypto import get_random_string

class SimpleTest(TestCase):
    def setUp(self):
        pass

    def test_parse_url_ads_true(self):
        the_campaign = get_random_string()
        the_content = get_random_string()
        the_medium = get_random_string()
        the_source = get_random_string()
        the_term = get_random_string()
        the_aclk = get_random_string()
        the_fbclid = get_random_string()
        the_gclid = get_random_string()
        the_msclkid = get_random_string()
        the_twclid = get_random_string()
        url = f"/?a=b&utm_campaign={the_campaign}&utm_medium={the_medium}&utm_content={the_content}&c=1&utm_term={the_term}&utm_source={the_source}&gclid={the_gclid}&fbclid={the_fbclid}&twclid={the_twclid}&msclkid={the_msclkid}&aclk={the_aclk}"
        response = self.client.get(url)
        objects = UTM.objects.all()
        self.assertEqual(len(objects), 1)
        object = objects[0]
        self.assertEqual(object.campaign, the_campaign)
        self.assertEqual(object.content, the_content)
        self.assertEqual(object.medium, the_medium)
        self.assertEqual(object.source, the_source)
        self.assertEqual(object.term, the_term)
        self.assertTrue(object.aclk)
        self.assertTrue(object.fbclid)
        self.assertTrue(object.gclid)
        self.assertTrue(object.msclkid)
        self.assertTrue(object.twclid)
        self.assertNotEqual("-", object.session_id)

    def test_parse_url_ads_false(self):
        the_campaign = get_random_string()
        the_content = get_random_string()
        the_medium = get_random_string()
        the_source = get_random_string()
        the_term = get_random_string()
        url = f"/?a=b&utm_campaign={the_campaign}&utm_medium={the_medium}&utm_content={the_content}&c=1&utm_term={the_term}&utm_source={the_source}"
        response = self.client.get(url)
        objects = UTM.objects.all()
        self.assertEqual(len(objects), 1)
        object = objects[0]
        self.assertEqual(object.campaign, the_campaign)
        self.assertEqual(object.content, the_content)
        self.assertEqual(object.medium, the_medium)
        self.assertEqual(object.source, the_source)
        self.assertEqual(object.term, the_term)
        self.assertFalse(object.aclk)
        self.assertFalse(object.fbclid)
        self.assertFalse(object.gclid)
        self.assertFalse(object.msclkid)
        self.assertFalse(object.twclid)
        self.assertNotEqual("-", object.session_id)
