from datetime import datetime, timezone
from random import randint

from django.contrib.auth.models import User
from django.urls import reverse
from django.db import models

from transport_nantes.settings_local import TOPIC_BLOG_EDIT_WINDOW_SECONDS
from mailing_list.models import MailingList

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
    # Obsolete, but removing the model doesn't remove the table,
    # which leaves a strange trace behind.


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
    #   publication_date
    #   template
    #   user

    # Provide the names of fields that the user may set but that do
    # not impede publication.
    optional_fields_for_publication = set().union(
        ['header_description',
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
# which encodes a name, publication date (we serve the item only if
# published), and satellite information (which is embedded in TBItem,
# because that seems easier with django than creating satellite
# classes for presentation, social media, content, etc.).
#
# Thus, a modification of a TBItem is simply a new TBItem that
# contains some of the things the old one did as well as something
# new.


class TopicBlogObjectBase(models.Model):

    """
    Represent all that is common in various the various
    TopicBlogObjects (Item, Email, etc.).
    """

    class Meta:
        abstract = True

    # I think I saw problems with unicode URLs, though.
    slug = models.SlugField(allow_unicode=True, blank=True)

    # Publication signals that the TBObject may be served to
    # non-privileged users.  A NULL or future publication_date
    # indicates the object should not be served to non-auth'd users.
    #
    # At most one of a collection of TBObjects of the same type and
    # with the same slug should be published.  More than one is an
    # error.
    #
    # The first_publication_date helps us understand collection life
    # cycle.  The modification date helps us understand object life
    # cycle.
    #
    # We call an unpublished object a draft (brouillon).
    # We call a published object published (publiée).
    # We call a published and then unpublished object retired (retirée).
    #
    # One should assume that drafts and retired objects may be deleted
    # in some asyncrhonous manner by a cleanup process running outside
    # of django itself, although we don't currently do so.
    publication_date = models.DateTimeField(blank=True, null=True)
    first_publication_date = models.DateTimeField(blank=True, null=True)
    date_modified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)

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

    def set_social_context(self, context):
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
                f'ID : {str(self.id)}'
        else:
            return f'{str(self.title)} - ID : {str(self.id)} (NO SLUG)'

    def get_servable_status(self):
        """Return True if page is user visible, False otherwise."""
        if self.publication_date is None or \
                datetime.now(timezone.utc) < self.publication_date:
            return False
        return True


######################################################################
# TopicBlogItem

class TopicBlogItem(TopicBlogObjectBase):

    """Represent an item in the TopicBlog.

    An item is the central user-visible element of a TopicBlog (TB)
    entry.

    """
    class Meta:
        permissions = (
            # The simpleset permission allows a user to view TBItems
            # that are draft or retired.
            ("tbi.may_view", "May view unpublished TopicBlogItems"),

            # Granting edit permission to users does not in itself
            # permit them to publish or retire, so it is reasonably
            # safe.
            ("tbi.may_edit", "May create and modify TopicBlogItems"),

            # Finally, we can grant users permission to publish, to
            # self-publish (implies tbi_may_publish), to self-retire,
            # and to retire (implies self-retire).  Permission to
            # retire implies permission to re-publish.
            ("tbi.may_publish", "May publish TopicBlogItems"),
            ("tbi.may_publish_self", "May publish own TopicBlogItems"),
            ("tbi.may_retire_self", "May retire own TopicBlogItems"),
            ("tbi.may_retire", "May retire TopicBlogItems"),
        )


    # Content Type ##################################################
    #
    # Encode what type of object we mean to be displaying.
    #
    # Examples are blog articles, newsletters (mailed or web viewed),
    # and petitions.
    content_type = models.ForeignKey(TopicBlogContentType,
                                     on_delete=models.CASCADE)

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


    def get_absolute_url(self):
        """This function is called on creation of the item"""
        if self.slug:
            return reverse("topicblog:view_item_by_pkid",
                           kwargs={"pkid": self.pk,
                                   "the_slug": self.slug})
        else:
            return reverse("topicblog:view_item_by_pkid_only",
                           kwargs={"pkid": self.pk})

    def get_edit_url(self):
        """This function returns a link leading to
        the edition page of an item."""
        if not self.slug:
            return reverse("topicblog:edit_item_by_pkid",
                           kwargs={"pkid": self.pk})
        else:
            return reverse("topicblog:edit_item",
                           kwargs={"pkid": self.pk,
                                   "the_slug": self.slug})

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

        The caller is responsable for retiring any same-slug item that
        is already published.

        It would manifestly be better to do the two together in a transaction.
        Cf. https://docs.djangoproject.com/en/3.2/topics/db/transactions/

        """
        if self.is_publishable():
            if self.first_publication_date is None:
                self.first_publication_date = datetime.now()
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

    def get_image_fields(self) -> list:
        """
        Return the names of fields that are Django ImageFields
        """
        all_fields = self._meta.get_fields()
        image_fields = list()
        for field in all_fields:
            if isinstance(field, models.ImageField):
                image_fields.append(field.name)

        return image_fields


######################################################################
# TopicBlogEmail

class TopicBlogEmail(TopicBlogObjectBase):
    """Represent an email.

    This can be rendered as an email to be sent or as a web page that
    the user clicks (or shares) with exactly the same content.

    Note that many fields are nullable in order to permit saving
    drafts during composition.  Publication and sending, however, must
    validate that all necessary fields are provided.

    This model must be marked immutable.  That's hard to enforce, but
    changes must only be spelling and typographical fixes.  If we send
    a mail, we can't have the web version change in the mean time.

    The header_image only displays on the website, not in emails.  A
    good way to make an email stay unread is to begin with an image so
    that the user doesn't see what's coming.

    """
    class Meta:
        permissions = (
            # The simpleset permission allows a user to view TBEmails
            # that are draft or retired.
            ("tbe.may_view", "May view unpublished TopicBlogEmails"),

            # Granting edit permission to users does not in itself
            # permit them to publish or retire, so it is reasonably
            # safe.
            ("tbe.may_edit", "May create and modify TopicBlogEmails"),

            # Finally, we can grant users permission to publish, to
            # self-publish (implies tbe_may_publish), to self-retire,
            # and to retire (implies self-retire).  Permission to
            # retire implies permission to re-publish.
            ("tbe.may_publish", "May publish TopicBlogEmails"),
            ("tbe.may_publish_self", "May publish own TopicBlogEmails"),
            ("tbe.may_send", "May send TopicBlogEmails"),
            ("tbe.may_send_self", "May send own TopicBlogEmails"),
        )

    subject = models.CharField(max_length=80, blank=True)
    header_image = models.ImageField(
        upload_to='header/', blank=True,
        help_text='résolution recommandée : 1600x500')

    # Content #######################################################
    body_text_1_md = models.TextField(blank=True)
    cta_1_slug = models.SlugField(blank=True)
    cta_1_label = models.CharField(max_length=100, blank=True)
    body_image_1 = models.ImageField(
        upload_to='body/', blank=True,
        help_text='résolution recommandée : 1600x500')
    body_image_1_alt_text = models.CharField(max_length=100, blank=True)

    body_text_2_md = models.TextField(blank=True)
    cta_2_slug = models.SlugField(blank=True)
    cta_2_label = models.CharField(max_length=100, blank=True)
    body_image_2 = models.ImageField(
        upload_to='body/', blank=True,
        help_text='résolution recommandée : 1600x500')
    body_image_2_alt_text = models.CharField(max_length=100, blank=True)

    # Plus slug, template, title, comment, and social media fields,
    # provided through abstract base class.


class TopicBlogEmailSendRecord(models.Model):

    """Represent the fact that we sent an email.
    """
    slug = models.SlugField(allow_unicode=True, blank=True)
    mailinglist = models.ForeignKey(MailingList, on_delete=models.PROTECT)
    recipient =  models.ForeignKey(User, on_delete=models.PROTECT)
    send_time = models.DateTimeField(auto_now=True)
    # Open time is the time of the first instance of a beacon responding.
    open_time = models.DateTimeField()
    # Click time is the time of the first instance of a link being clicked.
    click_time = models.DateTimeField()
    # Unsubscribe time is the first instance of a user clicking the
    # unsubscribe button, whether the unsubscribe is successful or
    # not.  Note that we still have to send the user to the
    # appropriate mailinglist unsubscribe page with user_id filled in
    # (so that no email confirmation is required, which would be safer
    # but would annoy most people).
    unsubscribe_time = models.DateTimeField()


class TopicBlogEmailClicks(models.Model):

    """Represent the fact that an email was clicked.

    Note that TopicBlogEmailSendRecord will record the first click,
    but here we want to record all clicks that happen and where they
    lead.

    """
    email = models.ForeignKey(TopicBlogEmailSendRecord, on_delete=models.PROTECT)
    click_time = models.DateTimeField()
    click_url = models.CharField(max_length=1024, blank=False)
