from django.test import TestCase

# Create your tests here.
class SimpleTest(TestCase):

    def test_main_page_status_code(self):
        response = self.client.get("/")
        return self.assertEqual(response.status_code, 200)
    
    