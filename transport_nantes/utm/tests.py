from django.test import TestCase
from .models import UTM
from django.utils.crypto import get_random_string

# This is used for creating probably distinct test values.
# It has no other real significance in this test.
k_string_length = 12


class SimpleTest(TestCase):
    def setUp(self):
        pass

    def test_parse_url_ads_true(self):
        the_campaign = get_random_string(k_string_length)
        the_content = get_random_string(k_string_length)
        the_medium = get_random_string(k_string_length)
        the_source = get_random_string(k_string_length)
        the_term = get_random_string(k_string_length)
        the_aclk = get_random_string(k_string_length)
        the_fbclid = get_random_string(k_string_length)
        the_gclid = get_random_string(k_string_length)
        the_msclkid = get_random_string(k_string_length)
        the_twclid = get_random_string(k_string_length)
        url = (
            f"/?a=b&utm_campaign={the_campaign}&"
            f"utm_medium={the_medium}"
            f"&utm_content={the_content}"
            f"&c=1&utm_term={the_term}"
            f"&utm_source={the_source}"
            f"&gclid={the_gclid}"
            f"&fbclid={the_fbclid}"
            f"&twclid={the_twclid}"
            f"&msclkid={the_msclkid}"
            f"&aclk={the_aclk}"
        )
        self.client.get(url)
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
        the_campaign = get_random_string(k_string_length)
        the_content = get_random_string(k_string_length)
        the_medium = get_random_string(k_string_length)
        the_source = get_random_string(k_string_length)
        the_term = get_random_string(k_string_length)
        url = (
            f"/?a=b&utm_campaign={the_campaign}"
            f"&utm_medium={the_medium}"
            f"&utm_content={the_content}"
            f"&c=1&utm_term={the_term}"
            f"&utm_source={the_source}"
        )
        self.client.get(url)
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

    def test_parse_user_input_with_amp(self):
        url = (
            "/tb/p/suite-president-republique-rer-dans-dix-villes/"
            "&data=05|01|Magazine44@loire-atlantique.fr"
            "|a533c2de6dec4fc952e808dad1501b18\ " # noqa
            "|beecb8f7d08247d6bcd90516d6628b41|0|0|638052439229581676|Unknown"
            "|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwi"
            "LCJXVCI6Mn0=|1000|||"
            "&sdata=pnSFPZfvqCsxyHKa4I3kiD8TbpBj1FMqXUfy6dWxfUQ=&reserved=0"
        )
        self.client.get(url)
        objects = UTM.objects.all()
        self.assertEqual(len(objects), 1)
        object = objects[0]
        self.assertEqual(
            object.base_url,
            "/tb/p/suite-president-republique-rer-dans-dix-villes/"
        )
