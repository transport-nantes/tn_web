from django.db import models

class TopicBlog(models.Model):
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
    body1_md = models.TextField()
    body2_md = models.TextField()

    # Images and presentation.
    # The template should be one of UNIQUE(template).
    template = models.CharField(max_length=80)
    # hero_image = ImageField()
    hero_text = models.CharField(max_length=80)
    
    # Social media.
    meta_description = models.TextField()
    twitter_title = models.CharField(max_length=80)
    twitter_description = models.TextField()

    og_title = models.CharField(max_length=80)
    og_description = models.TextField()

    def __str__(self):
        return 'self'
