from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException


class PressMention(models.Model):
    class Meta:
        permissions = (
            # Allow the user to see list view and create article
            ("press-editor", "May create and see list view Article"),
        )
        ordering = ['-article_publication_date', 'newspaper_name']

    newspaper_name = models.CharField(max_length=200)
    article_link = models.URLField(max_length=255)
    article_title = models.CharField(max_length=200)
    article_summary = models.TextField()
    article_publication_date = models.DateField()

    def __str__(self):
        return f"{self.newspaper_name} {self.article_title}"


class OpenGraphTwitter(models.Model):
    press_mention = models.ForeignKey(PressMention, on_delete=models.CASCADE)
    og_title = models.CharField(max_length=255, blank=True)
    og_description = models.TextField(blank=True)
    og_image = models.URLField(max_length=255, blank=True)
    twitter_title = models.CharField(max_length=255, blank=True)
    twitter_description = models.TextField(blank=True)
    twitter_image = models.URLField(max_length=255, blank=True)
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.press_mention.newspaper_name} {self.press_mention.article_title}"


@receiver(post_save, sender=PressMention)
def add_og_twitter_data(sender, instance, created, **kwargs):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-extensions")
    selenium = WebDriver(ChromeDriverManager().install(),
                         options=options)
    og_twitter_list_xpath = ["//meta[@property='og:title']",
                             "//meta[@property='og:description']",
                             "//meta[@property='og:image']",
                             "//meta[@property='twitter:title']",
                             "//meta[@property='twitter:description']",
                             "//meta[@property='twitter:image']"]
    selenium.get(instance.article_link)
    content_list = list()
    for xpath in og_twitter_list_xpath:
        try:
            og_twitter_meta_tag = selenium.find_element_by_xpath(xpath)
            content_list.append(og_twitter_meta_tag.get_attribute("content"))
        except NoSuchElementException:
            content_list.append("")
    selenium.quit()
    if created:
        og_twitter = \
            OpenGraphTwitter.objects.create(press_mention=instance,
                                            og_title=content_list[0],
                                            og_description=content_list[1],
                                            og_image=content_list[2],
                                            twitter_title=content_list[3],
                                            twitter_description=content_list[4],
                                            twitter_image=content_list[5])
    og_twitter.save()
