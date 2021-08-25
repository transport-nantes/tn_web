from django.db import models
from random import randint
from django.contrib.auth.models import User
from django.urls import reverse


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
        social['twitter_title'] = self.twitter_title
        social['twitter_description'] = self.twitter_description
        social['twitter_image'] = self.twitter_image

        social['og_title'] = self.og_title
        social['og_description'] = self.og_description
        social['og_image'] = self.og_image

        context['social'] = social

    def __str__(self):
        return '{topic} / {slug}'.format(topic=self.topic, slug=self.slug)

######################################################################
# topic blog, v2


class TopicBlogTemplate(models.Model):
    """Encode template metadata for displaying TB content.

    More precisely, we want to encode data useful for content editing
    so that we know what fields to display.  So this just provides a
    map of what fields are active for a given template.

    It's initially intended that TBTemplates will only be created by
    admins in the admin interface.  They are rather sensitive, in the
    sense that borking a template will bork all content that depends
    on the template.

    Note that creating the html template is a standard git action:
    create, edit, commit, PR.  So designers can do that part with no
    worry.  This model provides an interface between the html template
    and the TB editors so that users re asked for the fields that
    matter to the actions they are performing.

    At some point we might want to make this more publicly accessible,
    but probably we'll so seldom make new templates that the burden on
    devs will be light and not worth the development cost of making
    instances of this model safe to edit.

    With the exception of the template_name field, this model is
    largely a placeholder for now to remind us of what we want to
    happen eventually.  The first iteration of TBv2 will ask users for
    all fields possible.  We'll make it more use friendly once it
    works.

    I think we will want to have content be inserted via templatetags
    in order to facilitate automated content serving.  But for now,
    we'll assume we have a template file that defines an entire page.
    (We'll therefore need a single record in the database to represent
    that.)

    """
    # The template_name must be a valid html template name to pass to
    # django's render() function.
    template_name = models.CharField(max_length=80)
    # Provide a field for free-form comments from humans, who can note
    # their intent on creating the model.
    comment = models.TextField()

    # And now somehow we need to specify the fields.  Either we do
    # that with an explicit list of fields or, probably better, a
    # one-to-many relationship to TBTemplateFields.  And that model
    # will just have field name and a link back here.
    #
    # We could someday want to be fancy and provide field type and
    # such here so that content editors can build themselves instead
    # of just switching on and off preset fields.

    # Not yet functional. ##

# The way to think of TopicBlog (TB) is as a collection of TBItem's,
# which encodes a name, servability (whether or not we propose the
# item for serving), and satellite information (which is embedded in
# TBItem, because that seems easier with django than creating
# satellite classes for presentation, social media, content, etc.).
#
# Thus, a modification of a TBItem is simply a new TBItem that
# contains some of the things the old one did as well as something
# new.  For example, to make a variant of a TBItem with new social
# media info, we would duplicate the TBItem, replace the social media
# fields, and persist the new TBItem with the one changed data.
#
# All servable items with the same slug are potentially servable when
# a user requests that slug.  More specifically, they should be
# considered not just close or related but legitimately
# interchangeable.  In fact, we use the TBItem's item_sort_key to
# simplify serving.  Rather than doing multiple queries to learn how
# many items have the same slug and choosing one at random, we let a
# periodic process set the item_sort_key's to new random values.  On
# requesting a slug, we select the slug with the maximum
# item_sort_key.

    def __str__(self):
        return str(self.template_name) + " - " + str(self.comment)


class TopicBlogItem(models.Model):
    """Represent an item in the TopicBlog.

    An item is the central user-visible element of a TopicBlog (TB)
    entry.

    """
    # I think I saw problems with unicode URLs, though.
    slug = models.SlugField(allow_unicode=True, blank=True)
    item_sort_key = models.IntegerField()
    servable = models.BooleanField(default=True)
    published = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    # Presentation ##################################################
    #
    # Encode the basic structure of a TBItem's presentation.
    template = models.ForeignKey(TopicBlogTemplate, on_delete=models.PROTECT)
    # The HTML document <title>.
    title = models.CharField(max_length=100)
    # The header is the (optional) large full-width image, possibly
    # with some overlaying text, that appears at the top of many
    # pages.
    header_image = models.ImageField(blank=True)
    header_title = models.CharField(max_length=80, blank=True)
    header_description = models.CharField(max_length=120, blank=True)
    # The header_slug points to an existing TBItem slug and will
    # render as a link to that page.  That is, it is a way to encode
    # "what happens if a user clicks on this header?".
    header_slug = models.CharField(max_length=100, blank=True)

    # Content Type ##################################################
    #
    # Encode what type of object we mean to be displaying.
    #
    # Examples are blog articles, newsletters (mailed or web viewed),
    # and petitions.
    #
    # This should assuredly be based on an enum.  For the moment,
    # let's assume everything is an article.  Types we expect
    # eventually are article, project (square), press release,
    # newsletter, newsletter web (the "if you want to display this in
    # your browser" version), petitions, mailing list signup pages.
    content_choices = [("article", "article"),
                       ("project", "project"),
                       ("press_release", "press_release"),
                       ("newsletter", "newsletter"),
                       ("newsletter_web", "newsletter_web"),
                       ("petition", "petition"),
                       ("mailing_list_signup",
                       "mailing_list_signup"),
                       ]
    item_type = models.CharField(max_length=100, choices=content_choices,
                                 default="article")
    # Content #######################################################
    #
    # Encode the editorial content of a TBItem.
    #
    # We are encoding that content is some text and a CTA (and maybe
    # the same again), an image, and then maybe another bit of text
    # with a CTA.
    body_text_1_md = models.TextField(blank=True)
    cta_1_slug = models.SlugField(blank=True)
    cta_1_label = models.CharField(max_length=100, blank=True)
    body_text_2_md = models.TextField(blank=True)
    cta_2_slug = models.SlugField(blank=True)
    cta_2_label = models.CharField(max_length=100, blank=True)

    body_image = models.ImageField(blank=True)
    body_image_alt_text = models.CharField(max_length=100, blank=True)

    body_text_3_md = models.TextField(blank=True)
    cta_3_slug = models.SlugField(blank=True)
    cta_3_label = models.CharField(max_length=100, blank=True)

    # Social media ##################################################
    #
    # We'll want to encode somewhere the recommended image sizes for
    # different social media.  And if the user only specs one social
    # network, we should do our best to provide data for the others.

    # Optional editor notes about what this social data is trying to do.
    social_description = models.TextField(blank=True)

    twitter_title = models.CharField(max_length=80, blank=True)
    twitter_description = models.TextField(blank=True)
    twitter_image = models.CharField(max_length=100, blank=True)

    og_title = models.CharField(max_length=80, blank=True)
    og_description = models.TextField(blank=True)
    og_image = models.CharField(max_length=100, blank=True)

    def set_context(self, context):
        """
        inherited from original TB, it adds socials related
        fields to the context["social"] entry of the context dict.
        """
        social = {}
        social['twitter_title'] = self.twitter_title
        social['twitter_description'] = self.twitter_description
        social['twitter_image'] = self.twitter_image

        social['og_title'] = self.og_title
        social['og_description'] = self.og_description
        social['og_image'] = self.og_image

        context['social'] = social
        return context

    def __str__(self):
        if self.slug:
            return f'{str(self.slug)} - {str(self.title)} - \
                    ISK : {str(self.item_sort_key)} - ID : {str(self.id)}'
        else:
            return f'{str(self.title)} - ISK : {str(self.item_sort_key)} \
                    - ID : {str(self.id)} (NO SLUG)'

    def get_absolute_url(self):
        """This function is called on creation of the item"""
        if self.slug:
            return reverse("topicblog:view_item_by_pkid",
                           kwargs={"pkid": self.pk,
                                   "item_slug": self.slug})
        else:
            return self.get_edit_url()

    def get_edit_url(self):
        """This function returns a link leading to
        the edition page of an item."""
        if not self.slug:
            return reverse("topicblog:edit_item_no_slug",
                           kwargs={"pkid": self.pk})
        else:
            return reverse("topicblog:edit_item",
                           kwargs={"pkid": self.pk,
                                   "item_slug": self.slug})
