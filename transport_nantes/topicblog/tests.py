from django.test import TestCase
from .models import TopicBlogPage

# Create your tests here.
class SimpleTest(TestCase):

    def test_main_page_status_code(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 404)

        TopicBlogPage.objects.create(title="test", slug="test", topic="index", template="topicblog/2020_index.html")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)