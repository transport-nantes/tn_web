from datetime import datetime, timezone
from random import randint

from django.contrib.auth.models import User
from django.urls import reverse
from django.db import models

from transport_nantes.settings_local import TOPIC_BLOG_EDIT_WINDOW_SECONDS


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


class TopicBlogContentType(models.Model):
    """Provide a list of valid content types.

    Examples are article, petition, etc.
    """
    # Provide a (relatively) short name because this will appear in
    # dropdown lists in the TopicBlogItem editor.
    content_type = models.CharField(max_length=50)

    def __str__(self):
        return self.content_type


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
    # The template_name must be a valid filename of an html template
    # template to pass to django's render() function.
    template_name = models.CharField(max_length=80, unique=True)

    # Provide a field for free-form comments from humans, who can note
    # their intent on creating the model.
    comment = models.TextField()

    content_type = models.ForeignKey(TopicBlogContentType,
                                     on_delete=models.CASCADE)

    # These flags indicate which fields are involved in a
    # TopicBlogItem using this template instance.
    #
    # The fields are also required for publishing the TopicBlogItem
    # instance unless they are provided by the
    # optional_fields_for_publication() function.
    slug = models.BooleanField(default=False)
    title = models.BooleanField(default=False)
    header = models.BooleanField(default=False)
    body_text_1_md = models.BooleanField(default=False)
    cta_1 = models.BooleanField(default=False)
    body_text_2_md = models.BooleanField(default=False)
    cta_2 = models.BooleanField(default=False)
    body_image = models.BooleanField(default=False)
    body_text_3_md = models.BooleanField(default=False)
    cta_3 = models.BooleanField(default=False)
    social_media = models.BooleanField(default=False)

    # Flags not provided because not user-editable or that otherwise
    # make no sense to include.
    #
    #   item_sort_key
    #   servable
    #   published
    #   publication_date
    #   template
    #   user

    # Provide the names of fields that the user may set but that do
    # not impede publication.
    optional_fields_for_publication = set().union(
        ['header_description', 'header_slug',
         'cta_1_slug', 'cta_1_label',
         'cta_2_slug', 'cta_2_label',
         'cta_3_slug', 'cta_3_label',
         'body_image', 'body_image_alt_text',
         'twitter_title', 'twitter_description',
         'twitter_image', 'og_title',
         'og_description', 'og_image'])

    # Fields that, if required for publication, the requirement is
    # satisfied by providing any one of them.
    one_of_fields_for_publication = [
        ['body_text_1_md', 'body_text_2_md', 'body_text_3_md'],
        ['header_title', 'header_description'],
    ]

    # Dependent fields: if one in a group is provided, the others must
    # be as well before we can publish.
    dependent_field_names = [
        ['cta_1_slug', 'cta_1_label'],
        ['cta_2_slug', 'cta_2_label'],
        ['cta_3_slug', 'cta_3_label'],
        ['body_image', 'body_image_alt_text'],
    ]

    def __str__(self):
        return self.template_name


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


class TopicBlogItem(models.Model):

    """Represent an item in the TopicBlog.

    An item is the central user-visible element of a TopicBlog (TB)
    entry.

    """
    # I think I saw problems with unicode URLs, though.
    slug = models.SlugField(allow_unicode=True, blank=True)
    item_sort_key = models.IntegerField()
    # Servable items are those who are published and still reachable.
    # An item starts as unservable, and becomes servable when it is
    # published. If servable, it will be able to be reached from
    # the public.
    # If a published item is set to unservable, trying to access it
    # will result in a 404 .
    servable = models.BooleanField(default=False)
    # An item isn't considered published until it has a publication
    # date. Once published, it can't be unpublished.
    # An item to be both published and servable to be accessible to
    # the public.
    publication_date = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    # Content Type ##################################################
    #
    # Encode what type of object we mean to be displaying.
    #
    # Examples are blog articles, newsletters (mailed or web viewed),
    # and petitions.
    content_type = models.ForeignKey(TopicBlogContentType,
                                     on_delete=models.CASCADE)

    # Presentation ##################################################
    #
    # Encode the basic structure of a TBItem's presentation.
    template = models.ForeignKey(TopicBlogTemplate, on_delete=models.PROTECT)
    # The HTML document <title>.
    title = models.CharField(max_length=100, blank=True)
    # The header is the (optional) large full-width image, possibly
    # with some overlaying text, that appears at the top of many
    # pages.
    header_image = models.ImageField(
        upload_to='header/', blank=True,
        help_text='résolution recommandée : 1600x500')
    header_title = models.CharField(max_length=80, blank=True)
    header_description = models.CharField(max_length=120, blank=True)
    # The header_slug points to an existing TBItem slug and will
    # render as a link to that page.  That is, it is a way to encode
    # "what happens if a user clicks on this header?".
    header_slug = models.CharField(max_length=100, blank=True)

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

    body_image = models.ImageField(
        upload_to='body/', blank=True,
        help_text='résolution recommandée : 1600x500')
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
    social_description = models.TextField(
        blank=True,
        help_text='Notes pour humains des objectifs (marketing) de la page')

    twitter_title = models.CharField(max_length=80, blank=True)
    twitter_description = models.TextField(blank=True)
    twitter_image = models.ImageField(
        upload_to='twitter/', blank=True,
        help_text='2:1, résolution minimum : 300x157, max 4096x4096')
    # Cf. https://developer.twitter.com/en/docs/twitter-for-websites/cards/overview/summary-card-with-large-image # noqa

    og_title = models.CharField(max_length=80, blank=True)
    og_description = models.TextField(blank=True)
    og_image = models.ImageField(
        upload_to='opengraph/', blank=True,
        help_text='résolution recommandée : 1200x630')
    # Cf. https://iamturns.com/open-graph-image-size/
    # Cf. https://developers.facebook.com/docs/sharing/best-practices/
    # Cf. https://www.facebook.com/business/help/469767027114079?id=271710926837064 # noqa

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
            return f'{str(self.slug)} - {str(self.title)} - ' + \
                f'ISK : {str(self.item_sort_key)} - ID : {str(self.id)}'
        else:
            return f'{str(self.title)} - ISK : {str(self.item_sort_key)} ' + \
                f'- ID : {str(self.id)} (NO SLUG)'

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
            return reverse("topicblog:edit_item_by_pkid",
                           kwargs={"pkid": self.pk})
        else:
            return reverse("topicblog:edit_item",
                           kwargs={"pkid": self.pk,
                                   "item_slug": self.slug})

    def can_create_variant(self) -> bool:
        """
        Checks if the user can create a variant or not.
        Users can create variants at any time, unless the form
        is about a new item.
        """
        return True if self.id else False

    def is_editable(self) -> bool:
        """
        Checks if the user can edit the item or not.
        Users can edit the item at any time, unless the item
        has been published for more than a set amount of time.
        """
        is_editable = True
        if self.publication_date:
            # Checks to allow the user to edit the item or not
            time_since_publication = datetime.now(
                timezone.utc) - self.publication_date

            # Beyond X seconds, the user can't edit the item anymore
            # and only has the possibility to create a variant.
            seconds_since_publication_date = time_since_publication.seconds
            if seconds_since_publication_date > TOPIC_BLOG_EDIT_WINDOW_SECONDS:
                is_editable = False

        return is_editable

    def is_publishable(self) -> bool:
        """
        Return True if the item may be published.

        An item may be published if it has no missing required fields,
        as defined by the related TopicBlogTemplate.
        """
        if self.get_missing_publication_field_names():
            return False
        return True

    def publish(self):
        """
        If publishable, set item publication and return True.
        Else do nothing and return False.
        """
        if self.is_publishable():
            self.servable = True
            self.publication_date = datetime.now()
            return True
        else:
            return False

    def get_missing_publication_field_names(self) -> set:
        """
        This function returns a list of all missing fields
        for publication.

        If no content is present in any of the content dedicated
        fields (eg. 'body_text_1_md', 'body_text_2_md', 'body_text_3_md',
        'body_image'), 'content' is also added to the list.
        """
        template = self.template
        missing_field_names = set()
        required_field_names = self.get_participating_field_names().\
            difference(template.optional_fields_for_publication)

        for field_name in required_field_names:
            if not getattr(self, field_name):
                missing_field_names.add(field_name)

        # This will mark all fields in each set as missing if the set
        # constraint isn't satisfied.  This is something to signal to
        # users.  Getting this feedback perfect requires some thought
        # and experience using the tool.
        #
        # Of course, for now we aren't even providing feedback, so
        # this comment is ahead of its time.
        for field_name_set in template.one_of_fields_for_publication:
            one_provided = False
            for field_name in field_name_set:
                if field_name not in missing_field_names:
                    one_provided = True
            if one_provided:
                missing_field_names = missing_field_names.difference(
                    field_name_set)
            else:
                missing_field_names = missing_field_names.union(field_name_set)

        # This checks that dependent fields are either provided or not
        # together.  If a user provides some but not others, we'll
        # indicate that the entire set is missing, which isn't perfect
        # but is something we can sort later if it becomes confusing
        # for users.  Initially, we should just make sure that our
        # user instructions note that we do this.
        for dependent_field_name_set in template.dependent_field_names:
            all_provided = True
            all_missing = True
            for field_name in dependent_field_name_set:
                if getattr(self, field_name):
                    all_missing = False
                else:
                    all_provided = False
            if not (all_provided or all_missing):
                missing_field_names = missing_field_names.union(
                    dependent_field_name_set)

        return missing_field_names

    def get_participating_field_names(self) -> set:
        """
        Return the names of fields that participate in this TopicBlogItem
        based on the Template it uses.

        This only provides user-settable fields.
        """
        template = self.template
        fields = set()
        if template.slug:
            fields.add('slug')
        if template.title:
            fields.add('title')
        if template.header:
            fields.add('header_image')
            fields.add('header_title')
            fields.add('header_description')
            fields.add('header_slug')
        if template.body_text_1_md:
            fields.add('body_text_1_md')
        if template.body_text_2_md:
            fields.add('body_text_2_md')
        if template.body_text_3_md:
            fields.add('body_text_3_md')
        if template.cta_1:
            fields.add('cta_1_slug')
            fields.add('cta_1_label')
        if template.cta_2:
            fields.add('cta_2_slug')
            fields.add('cta_2_label')
        if template.cta_3:
            fields.add('cta_3_slug')
            fields.add('cta_3_label')
        if template.body_image:
            fields.add('body_image')
            fields.add('body_image_alt_text')
        if template.social_media:
            fields.add('twitter_title')
            fields.add('twitter_description')
            fields.add('twitter_image')
            fields.add('og_title')
            fields.add('og_description')
            fields.add('og_image')
        return fields

    def get_slug_fields(self) -> list:
        """
        Return the names of fields that are Django SlugFields
        """
        all_fields = self._meta.get_fields()
        slug_fields = list()
        for field in all_fields:
            if isinstance(field, models.SlugField):
                slug_fields.append(field.name)

        return slug_fields

    def get_servable_status(self):
        """Return True if page is user visible, False otherwise."""
        if not self.servable:
            return False

        if self.publication_date is None or \
                datetime.now(timezone.utc) < self.publication_date:
            return False

        return True
