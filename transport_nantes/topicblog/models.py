from django.db import models
from django.db.models import Count
from random import randint

class TopicBlogPageManager(models.Manager):
    """Manager to help us query for records at random.

    https://web.archive.org/web/20110802060451/http://bolddream.com/2010/01/22/getting-a-random-row-from-a-relational-database/
    """

    def random_topic_member(self, topic):
        """Return a random record from the db.

        Usage: page = TopicBlogPage.objects.random(my_topic)
        """
        # print('rtm: ', topic)
        if True:
            # Temporary hack, be really, really inefficient.
            all_in_topic = self.filter(topic=topic)
            random_index = randint(0, all_in_topic.count() - 1)
            # print('random_index=', random_index)
            return all_in_topic[random_index]
        count = self.aggregate(ids=Count('id'), filter=Q(topic=topic))['ids']
        # print('rtm: ', count)
        random_index = randint(0, count - 1)
        # print('rtm: ', random_index)
        return self.all()[random_index]

class TopicBlogPage(models.Model):
    """Represent a blog entry that permits some measurement.

    We want to discover and measur what works and what doesn't.  So
    the idea is that we have topics and one or more pages servable
    under that topic.  All pages for a given topic should be
    semantically interchangeable, and internal links on our own blog
    should generally point to topics rather than specific pages.  This
    lets us measure what sorts of pages work well and what sorts
    don't.

    We have two important contexts: externally presented links (e.g.,
    shares) and internally presented links (within site).  In the
    first case, we're measuring using interaction with the page's
    social media preview information, such as twitter card or
    opengraph info.  To some extent, we'll also want to measure what
    causes the page to hold the reader's attention, to click further,
    eventually to convert.

    In the second case, we're measuring only retention and progress to
    goal.  So we generally want to distinguish between the two.
    Probably our only real way to do that is via REFERER, because any
    internal link can be copied and presented externally.

    """
    # The article.
    title = models.CharField(max_length=100)
    slug = models.SlugField(allow_unicode=True)
    # Topic should be a one of UNIQUE(topic).  That is, topic creation
    # should not be accidental due to typos.
    topic = models.SlugField(allow_unicode=True)

    # Body text as markdown.
    # Internal links are via topic slug.
    body1_md = models.TextField(blank=True)
    body2_md = models.TextField(blank=True)
    body3_md = models.TextField(blank=True)

    # Images and presentation.
    # The template should be one of UNIQUE(template).
    template = models.CharField(max_length=80)
    # hero_image = models.ImageField()
    hero_image = models.CharField(max_length=100, blank=True)
    hero_title = models.CharField(max_length=80, blank=True)
    hero_description = models.CharField(max_length=120, blank=True)
    # mid_image = models.ImageField()
    middle_image = models.CharField(max_length=100, blank=True)
    middle_image_alt = models.CharField(max_length=240, blank=True)
    # For pages that list several points with images and text.  If the
    # image and text are not both provided, we don't render the pair.
    bullet_image_1 = models.CharField(max_length=100, blank=True)
    bullet_text_1_md = models.TextField(blank=True)
    bullet_image_2 = models.CharField(max_length=100, blank=True)
    bullet_text_2_md = models.TextField(blank=True)
    bullet_image_3 = models.CharField(max_length=100, blank=True)
    bullet_text_3_md = models.TextField(blank=True)
    bullet_image_4 = models.CharField(max_length=100, blank=True)
    bullet_text_4_md = models.TextField(blank=True)
    bullet_image_5 = models.CharField(max_length=100, blank=True)
    bullet_text_5_md = models.TextField(blank=True)

    # Social media.
    meta_description = models.TextField(blank=True)
    twitter_title = models.CharField(max_length=80, blank=True)
    twitter_description = models.TextField(blank=True)
    twitter_image = models.CharField(max_length=100, blank=True)

    og_title = models.CharField(max_length=80, blank=True)
    og_description = models.TextField(blank=True)
    og_image = models.CharField(max_length=100, blank=True)

    objects = TopicBlogPageManager()

    def set_context(self, context):
        """Set context that the model can provide.

        """
        social = {}
        if self.twitter_title:
            social['twitter_title'] = self.twitter_title
        if self.twitter_description:
            social['twitter_description'] = self.twitter_description
        if self.twitter_image:
            social['twitter_image'] = self.twitter_image

        if self.og_title:
            social['og_title'] = self.og_title
        if self.og_description:
            social['og_description'] = self.og_description
        if self.og_image:
            social['og_image'] = self.og_image

        context['social'] = social

    def __str__(self):
        return '{topic} / {slug}'.format(topic=self.topic, slug=self.slug)
