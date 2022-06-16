from datetime import datetime, timezone
import logging

from django.contrib.auth.models import User
from django.forms import ValidationError
from django.urls import reverse
from django.db import models

from mailing_list.models import MailingList

logger = logging.getLogger("django")

######################################################################
# topic blog, v1


class TopicBlogPage(models.Model):
    """Obsolete.

    Removing the model doesn't remove the table, which leaves a
    strange trace behind.  This stub just explains a bit of history.

    """

    pass


######################################################################
# topic blog, v2


class TopicBlogContentType(models.Model):
    """Obsolete.

    Removing the model doesn't remove the table, which leaves a
    strange trace behind.  This stub just explains a bit of history.

    """

    pass


class TopicBlogTemplate(models.Model):
    """Obsolete.

    Removing the model doesn't remove the table, which leaves a
    strange trace behind.  This stub just explains a bit of history.

    """

    pass


class TopicBlogObjectBase(models.Model):

    """The base of all of TopicBlog.

    Represent a versioned object without social media support.
    """

    class Meta:
        abstract = True

    # I think I saw problems with unicode URLs, though.
    slug = models.SlugField(max_length=90, allow_unicode=True, blank=True)

    # Publication signals that the TBObject may be served to
    # non-privileged users.  A NULL or future publication_date
    # indicates the object should not be served to non-auth'd users.
    #
    # See below for historical notes, which may to some extent be a
    # current discription of the system.  We first describe what we
    # want the system to be doing.  Note that these variables are
    # called "_date" but are actually "_timestamp".
    #
    # * first_publication_date is set if this object is at some point
    #   in history published.  It is None if the object has never been
    #   published.  Once set, it should never change.
    #
    # * publication_date is the timestamp at which this object was
    #   last published.  Multiple objects with the same slug may have
    #   been published and so have non-empty publication_date.  The
    #   most recently published object is the servable version of a
    #   slug collection.
    #
    # * The modification date is the timestamp at which this object
    #   was last modified.
    #
    #
    # Historical notes:
    #
    # We used to define publication this way, and to some extent it
    # may still be true:
    #
    # * first_publication_date was the initial timestamp at which some
    #   object with this slug was published.
    #
    # * publication_date was the timestamp at which this object, if it
    #   is the currently servable object, was published.  At most one
    #   of a collection of TBObjects of the same type and with the
    #   same slug would be published.  More than one was an error.
    #
    # * The modification date was the timestamp on which this object
    #   was last modified.
    #
    # End historical notes.  When we believe these notes are purely
    # history and do not represent the state of the system, we should
    # delete this part of the comment section.
    #
    # We call an unpublished object a draft (brouillon).
    # We call the currently servable object published (publiée).
    # We call a published and then unpublished object retired (retirée).
    #
    # We call the collection of objects with the same slug a slug
    # collection.
    #
    # One should assume that objects that have never been published
    # may be deleted in some asyncrhonous manner by a cleanup process,
    # although we don't currently do so.
    publication_date = models.DateTimeField(blank=True, null=True)
    first_publication_date = models.DateTimeField(blank=True, null=True)
    date_modified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT,
                             related_name='+')
    publisher = models.ForeignKey(User, on_delete=models.PROTECT,
                                  related_name='+', blank=True, null=True)

    # Presentation ##################################################
    #
    # Encode the basic structure of a TBItem's presentation.
    template_name = models.CharField(max_length=80, blank=True)

    # The urls to create a new object of this class' children is a property
    # that has to be set in each new subclass.
    # It is expected to be a string with 'app:name' format. e.g.:
    # 'topicblog:new_item'
    new_object_url = None
    listone_object_url = None
    listall_object_url = None
    viewbyslug_object_url = None
    # The description is meant to be a really short string description
    # of what the object is supposed to render into.
    # e.g. a TopicBlogItem is a "Page de blog"
    # This is used as header in object-related forms
    description_of_object = None

    def __str__(self):
        if self.slug:
            return f'{str(self.slug)} - ' + \
                f'ID : {str(self.id)}'
        else:
            return f'{str(self.title)} - ID : {str(self.id)} (NO SLUG)'

    def get_servable_status(self):
        """Return True if page is user visible, False otherwise."""
        if self.publication_date is None or \
                datetime.now(timezone.utc) < self.publication_date:
            return False
        return True

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

    def is_publishable(self) -> bool:
        """
        Return True if the object may be published.

        An object may be published if it has no missing required fields,
        as defined in self.template_config
        """
        missing_fields = self.get_missing_publication_field_names()
        if missing_fields:
            logger.info(f"Can't publish, missing {missing_fields}")
            return False
        return True

    def publish(self):
        """
        If publishable, set object publication and return True.
        Else do nothing and return False.

        The caller is responsable for retiring any same-slug object that
        is already published.

        It would manifestly be better to do the two together in a transaction.
        Cf. https://docs.djangoproject.com/en/3.2/topics/db/transactions/

        """
        if self.is_publishable():
            now_timestamp = datetime.now(timezone.utc)
            if self.first_publication_date is None:
                self.first_publication_date = now_timestamp
                self.publication_date = now_timestamp
            else:
                self.publication_date = now_timestamp
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
        template = self.template_name
        template_cfg = self.template_config[template]
        optional_fields = template_cfg['optional_fields_for_publication']
        missing_field_names = set()
        required_field_names = self.get_participating_field_names().\
            difference(optional_fields)

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
        for field_name_set in template_cfg['one_of_fields_for_publication']:
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
        for dependent_field_name_set in template_cfg["dependent_field_names"]:
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
        Return the names of fields that participate in this TopicBlogObject
        based on the Template it uses.

        This only provides user-settable fields.
        """
        template = self.template_name
        template_cfg = self.template_config[template]

        fields = set()
        for field_name, value in template_cfg["fields"].items():
            if value:
                if field_name == "slug":
                    fields.add('slug')
                    continue
                if field_name == "title":
                    fields.add('title')
                    continue
                if field_name == "header":
                    fields.add('header_image')
                    fields.add('header_title')
                    fields.add('header_description')
                    continue
                if field_name == "social_media":
                    fields.add('twitter_title')
                    fields.add('twitter_description')
                    fields.add('twitter_image')
                    fields.add('og_title')
                    fields.add('og_description')
                    fields.add('og_image')
                    continue
        return fields


class TopicBlogObjectSocialBase(TopicBlogObjectBase):

    """Represent social media sharing data.

    Note that many fields are nullable in order to permit saving
    drafts during composition.  Publication and sending, however, must
    validate that all necessary fields are provided.

    """

    class Meta:
        abstract = True

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

    author_notes = models.TextField(
        help_text='Notes pour éditeurs : ne seront pas affichées sur le site',
        verbose_name="Notes libres pour éditeurs",
        blank=True, null=True)

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


class SendRecordBase(models.Model):
    """Base model for Send Records."""

    class Meta:
        abstract = True

    class StatusChoices(models.TextChoices):
        # Newly created objects derived from SendRecordBase start life
        # as PENDING.
        PENDING = 'PENDING', "Pending"
        # If SES indicates a non-permanent failure, the object enters
        # state RETRY.  From this state, it should eventually
        # transition to SENT or FAILED.
        RETRYING = 'RETRY', 'Retry'
        # Objects become SENT when SES accepts them (at handoff).
        # This is an absorbing state.
        SENT = 'SENT', "Sent"
        # If SES indicates a permanent failure, the object transitions
        # to FAILED.  This is an absorbing state.
        FAILED = 'FAILED', "Failed"

    recipient = models.ForeignKey(User, on_delete=models.PROTECT)
    status = models.CharField(
        max_length=50, choices=StatusChoices.choices,
        default=StatusChoices.PENDING)
    # The handoff time is the timestamp at which the function we use
    # to send mail returned without error.
    handoff_time = models.DateTimeField(null=True, blank=True)
    # The send time is the timestamp at which our email provider (SES
    # at the time of writing this comment) confirms that it has sent
    # the mail.
    send_time = models.DateTimeField(null=True, blank=True)
    # Open time is the time of the first instance of a beacon
    # responding.  Note that we may receive many beacon signals on a
    # single message.  We want to record here the first time we
    # receive one.
    open_time = models.DateTimeField(null=True, blank=True)
    # Click time is the time of the first instance of a link in the
    # mail being clicked.
    click_time = models.DateTimeField(null=True, blank=True)
    aws_message_id = models.CharField(max_length=300, blank=True, null=True)


class SendRecordTransactional(SendRecordBase):
    """Represent a transactional email.

    This class represents mail sent without a slug (i.e., not
    TopicBlog content.

    """
    pass


class SendRecordMarketing(SendRecordBase):
    """This cleass represents a marketing email.

    At a technical level, it differs from SendRecordTransactional by
    virtue of having a unique index on (slug, recipient), and because
    of that it is abstract because only derived classes will know what
    TBObject sub-type the slug points to.

    """

    class Meta:
        abstract = True

    # Slug to the article that was sent
    slug = models.SlugField(max_length=90, allow_unicode=True, blank=True)
    # A SendRecordMarketing represents a mail sent to a single
    # recipient.  We may have chosen this recipient, however, because
    # the person is subscribed to a mailing list, and so we need to
    # record that list here in order to be able to respond to
    # unsubscribe requests.
    mailinglist = models.ForeignKey(MailingList, on_delete=models.PROTECT)
    unsubscribe_time = models.DateTimeField(null=True, blank=True)


######################################################################
# TopicBlogItem

class TopicBlogItem(TopicBlogObjectSocialBase):

    """Represent a web blog page."""
    class Meta:
        permissions = (
            # The simpleset permission allows a user to view TBItems
            # that are draft or retired.
            ("tbi.may_view", "May view unpublished TopicBlogItems"),

            # Granting edit permission to users does not in itself
            # permit them to publish or retire, so it is reasonably
            # safe.
            ("tbi.may_edit", "May create and modify TopicBlogItems"),

            # Finally, we can grant users permission to publish and to
            # self-publish (implies tbi_may_publish)
            ("tbi.may_publish", "May publish TopicBlogItems"),
            ("tbi.may_publish_self", "May publish own TopicBlogItems"),
        )

    # Content Type ##################################################
    #
    # The content types match existing templates with their content type.
    # "content type": [list of templates available for this type]
    # The templates in the list must :
    # 1) Exist in the templates/ directory
    # 2) be configurated in self.template_config
    # Default values for template_config ###########################
    template_config_default = {
        "optional_fields_for_publication": (
            'header_image', 'header_description',
            'cta_1_slug', 'cta_1_label',
            'cta_2_slug', 'cta_2_label',
            'cta_3_slug', 'cta_3_label',
            'body_image', 'body_image_alt_text',
            'twitter_title', 'twitter_description',
            'twitter_image', 'og_title',
            'og_description', 'og_image',
        ),
        # Fields that, if required for publication, the requirement is
        # satisfied by providing any one of them.
        "one_of_fields_for_publication": [
            ['body_text_1_md', 'body_text_2_md', 'body_text_3_md'],
            ['header_title', 'header_description'],
        ],
        # Dependent fields: if one in a group is provided, the others must
        # be as well before we can publish.
        "dependent_field_names": [
            ['cta_1_slug', 'cta_1_label'],
            ['cta_2_slug', 'cta_2_label'],
            ['cta_3_slug', 'cta_3_label'],
            ['body_image', 'body_image_alt_text'],
        ],
    }
    template_config = {
        'topicblog/content.html': {
            'user_template_name': 'Article',
            'active': True,
            "fields": {
                'slug': True,
                'title': True,
                'header': True,
                'body_text_1_md': True,
                'cta_1': True,
                'body_text_2_md': True,
                'cta_2': True,
                'body_image': True,
                'body_text_3_md': True,
                'cta_3': True,
                'social_media': True,
            },
            "optional_fields_for_publication":
                template_config_default['optional_fields_for_publication'],
            "one_of_fields_for_publication":
                template_config_default['one_of_fields_for_publication'],
            "dependent_field_names":
                template_config_default['dependent_field_names'],
        },
        'topicblog/communique_presse_1.html': {
            'user_template_name': 'Communiqué de presse',
            'active': True,
            "fields": {
                'slug': True,
                'title': True,
                'header': False,
                'body_text_1_md': True,
                'cta_1': True,
                'body_text_2_md': True,
                'cta_2': True,
                'body_image': False,
                'body_text_3_md': True,
                'cta_3': True,
                'social_media': True,
            },
            "optional_fields_for_publication":
                template_config_default['optional_fields_for_publication'],
            "one_of_fields_for_publication":
                template_config_default['one_of_fields_for_publication'],
            "dependent_field_names":
                template_config_default['dependent_field_names'],
        }
    }
    # Content #######################################################
    #
    # Encode the editorial content of a TBItem.
    #
    # We are encoding that content is some text and a CTA (and maybe
    # the same again), an image, and then maybe another bit of text
    # with a CTA.
    body_text_1_md = models.TextField(blank=True)
    cta_1_slug = models.SlugField(max_length=90, blank=True)
    cta_1_label = models.CharField(max_length=100, blank=True)
    body_text_2_md = models.TextField(blank=True)
    cta_2_slug = models.SlugField(max_length=90, blank=True)
    cta_2_label = models.CharField(max_length=100, blank=True)

    body_image = models.ImageField(
        upload_to='body/', blank=True,
        help_text='résolution recommandée : 1600x500')
    body_image_alt_text = models.CharField(max_length=100, blank=True)

    body_text_3_md = models.TextField(blank=True)
    cta_3_slug = models.SlugField(max_length=90, blank=True)
    cta_3_label = models.CharField(max_length=100, blank=True)

    new_object_url = 'topicblog:new_item'
    listone_object_url = 'topicblog:list_items_by_slug'
    listall_object_url = 'topicblog:list_items'
    viewbyslug_object_url = 'topicblog:view_item_by_slug'
    description_of_object = 'Page de blog'

    def get_absolute_url(self):
        """Provide a link to view this object (by slug and id).
        """
        if self.slug:
            return reverse("topicblog:view_item_by_pkid",
                           kwargs={"pkid": self.pk,
                                   "the_slug": self.slug})
        else:
            return reverse("topicblog:view_item_by_pkid_only",
                           kwargs={"pkid": self.pk})

    def get_edit_url(self):
        """Provide a link to edit this object (by slug and id).
        """
        if not self.slug:
            return reverse("topicblog:edit_item_by_pkid",
                           kwargs={"pkid": self.pk})
        else:
            return reverse("topicblog:edit_item",
                           kwargs={"pkid": self.pk,
                                   "the_slug": self.slug})

    def get_participating_field_names(self) -> set:
        """
        Return the names of fields that participate in this TopicBlogObject
        based on the Template it uses.

        This only provides user-settable fields.
        """
        fields = super().get_participating_field_names()
        template = self.template_name
        template_cfg = self.template_config[template]
        for field_name, value in template_cfg["fields"].items():
            if field_name == "body_text_1_md":
                fields.add('body_text_1_md')
                continue
            if field_name == "body_text_2_md":
                fields.add('body_text_2_md')
                continue
            if field_name == "body_text_3_md":
                fields.add('body_text_3_md')
                continue
            if field_name == "cta_1":
                fields.add('cta_1_slug')
                fields.add('cta_1_label')
                continue
            if field_name == "cta_2":
                fields.add('cta_2_slug')
                fields.add('cta_2_label')
                continue
            if field_name == "cta_3":
                fields.add('cta_3_slug')
                fields.add('cta_3_label')
                continue
            if field_name == "body_image":
                fields.add('body_image')
                fields.add('body_image_alt_text')
                continue
        return fields

######################################################################
# TopicBlogEmail


class TopicBlogEmail(TopicBlogObjectSocialBase):
    """Represent an email.

    This can be rendered as an email to be sent or as a web page that
    the user clicks (or shares) with exactly the same content.

    This object is conceptually immutable once published, in the sense
    that changes should only be spelling and typographical fixes.  If
    we send a mail, we shouldn't have the web version change in the
    mean time.

    The header_image only displays on the website, not in emails.
    (Is/should this still be true?)  A good way to make an email stay
    unread is to begin with an image so that the user doesn't see
    what's coming.

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
    # Plus slug, template, title, comment, and social media fields,
    # provided through abstract base class.

    template_config_default = {
        "optional_fields_for_publication": (
            'header_title',
            'header_image', 'header_description',
            'cta_1_slug', 'cta_1_label',
            'cta_2_slug', 'cta_2_label',
            'body_image_1', 'body_image_1_alt_text',
            'body_image_2', 'body_image_2_alt_text',
            'twitter_title', 'twitter_description',
            'twitter_image', 'og_title',
            'og_description', 'og_image',
        ),
        "one_of_fields_for_publication": [
            ['header_title', 'header_description'],
        ],
        # Dependent fields: if one in a group is provided, the others must
        # be as well before we can publish.
        "dependent_field_names": [
            ['body_image_1', 'body_image_1_alt_text'],
            ['body_image_2', 'body_image_2_alt_text'],
            ['cta_1_slug', 'cta_1_label'],
            ['cta_2_slug', 'cta_2_label'],
        ],
    }
    template_config = {
        'topicblog/content_email_client.html': {
            'user_template_name': 'Classic',
            'active': True,
            "fields": {
                'slug': True,
                'title': True,
                'subject': True,
                'body_text_1_md': True,
            },
            "optional_fields_for_publication":
                template_config_default['optional_fields_for_publication'],
            "one_of_fields_for_publication":
                template_config_default['one_of_fields_for_publication'],
            "dependent_field_names":
                template_config_default['dependent_field_names'],
        },
    }

    subject = models.CharField(max_length=80, blank=True)
    header_image = models.ImageField(
        upload_to='header/', blank=True,
        help_text='résolution recommandée : 1600x500')

    # Content #######################################################
    body_text_1_md = models.TextField(blank=True)
    cta_1_slug = models.SlugField(max_length=90, blank=True)
    cta_1_label = models.CharField(max_length=100, blank=True)
    body_image_1 = models.ImageField(
        upload_to='body/', blank=True,
        help_text='résolution recommandée : 1600x500')
    body_image_1_alt_text = models.CharField(max_length=100, blank=True)

    body_text_2_md = models.TextField(blank=True)
    cta_2_slug = models.SlugField(max_length=90, blank=True)
    cta_2_label = models.CharField(max_length=100, blank=True)
    body_image_2 = models.ImageField(
        upload_to='body/', blank=True,
        help_text='résolution recommandée : 1600x500')
    body_image_2_alt_text = models.CharField(max_length=100, blank=True)

    # Plus slug, template, title, comment, and social media fields,
    # provided through abstract base class.

    new_object_url = 'topicblog:new_email'
    listone_object_url = 'topicblog:list_emails_by_slug'
    listall_object_url = 'topicblog:list_emails'
    viewbyslug_object_url = 'topicblog:view_email_by_slug'
    send_object_url = 'topicblog:send_email'
    description_of_object = 'Email'

    def get_absolute_url(self):
        """Provide a link to view this object (by slug and id).
        """
        if self.slug:
            return reverse("topicblog:view_email_by_pkid",
                           kwargs={"pkid": self.pk,
                                   "the_slug": self.slug})
        else:
            return reverse("topicblog:view_email_by_pkid_only",
                           kwargs={"pkid": self.pk})

    def get_edit_url(self):
        """Provide a link to edit this object (by slug and id).
        """
        if not self.slug:
            return reverse("topicblog:edit_email_by_pkid",
                           kwargs={"pkid": self.pk})
        else:
            return reverse("topicblog:edit_email",
                           kwargs={"pkid": self.pk,
                                   "the_slug": self.slug})

    def get_participating_field_names(self) -> set:
        """
        Return the names of fields that participate in this TopicBlogObject
        based on the Template it uses.

        This only provides user-settable fields.
        """
        fields = super().get_participating_field_names()
        template = self.template_name
        template_cfg = self.template_config[template]
        for field_name, value in template_cfg["fields"].items():
            if field_name == "subject":
                fields.add('subject')
                continue
            if field_name == "body_text_1_md":
                fields.add('body_text_1_md')
                continue
            if field_name == "body_text_2_md":
                fields.add('body_text_2_md')
                continue
            if field_name == "cta_1":
                fields.add('cta_1_slug')
                fields.add('cta_1_label')
                continue
            if field_name == "cta_2":
                fields.add('cta_2_slug')
                fields.add('cta_2_label')
                continue
            if field_name == "body_image_1":
                fields.add('body_image_1')
                fields.add('body_image_1_alt_text')
                continue
            if field_name == "body_image_2":
                fields.add('body_image_2')
                fields.add('body_image_2_alt_text')
                continue
        return fields


class SendRecordMarketingEmail(SendRecordMarketing):
    """Represent the sending of a TBEmail.

    """

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipient', 'slug'],
                name='TBE_unique_recipient_slug')
        ]


class TopicBlogEmailClicks(models.Model):
    """Represent the fact that an email was clicked.

    Note that SendRecordMarketingEmail will record the first click,
    but here we want to record all clicks that happen and where they
    lead.

    """
    email = models.ForeignKey(SendRecordMarketingEmail,
                              on_delete=models.PROTECT)
    click_time = models.DateTimeField()
    click_url = models.CharField(max_length=1024, blank=False)


######################################################################
# TopicBlogPress

class TopicBlogPress(TopicBlogObjectSocialBase):
    """Represent a press release.

    This can be rendered as an email to be sent or as a web page that
    the user clicks (or shares) with exactly the same content.

    This object is conceptually immutable once published, in the sense
    that changes should only be spelling and typographical fixes.  If
    we send a mail, we shouldn't have the web version change in the
    mean time.

    The header_image only displays on the website, not in emails.
    (Is/should this still be true?)  A good way to make an email stay
    unread is to begin with an image so that the user doesn't see
    what's coming.

    """
    class Meta:
        permissions = (
            # The simpleset permission allows a user to view TBPress
            # that are draft or retired.
            ("tbp.may_view", "May view unpublished TopicBlogPress"),

            # Granting edit permission to users does not in itself
            # permit them to publish or retire, so it is reasonably
            # safe.
            ("tbp.may_edit", "May create and modify TopicBlogPress"),

            # Finally, we can grant users permission to publish, to
            # self-publish (implies tbp_may_publish), to send, and to
            # self-send.
            ("tbp.may_publish", "May publish TopicBlogPress"),
            ("tbp.may_publish_self", "May publish own TopicBlogPress"),
            ("tbp.may_send", "May send TopicBlogPresss"),
            ("tbp.may_send_self", "May send own TopicBlogPress"),
        )

    template_config_default = {
        "optional_fields_for_publication": (
            'header_title',
            'header_image', 'header_description',
            'body_image', 'body_image_alt_text',
            'twitter_title', 'twitter_description',
            'twitter_image', 'og_title',
            'og_description', 'og_image'
        ),
        "one_of_fields_for_publication": [
            ['header_title', 'header_description'],
        ],
        # Dependent fields: if one in a group is provided, the others must
        # be as well before we can publish.
        "dependent_field_names": [
            ['body_image_1', 'body_image_1_alt_text'],
        ],
    }
    template_config = {
        'topicblog/content_press_mail_client.html': {
            'user_template_name': 'Classic',
            'active': True,
            "fields": {
                'slug': True,
                'title': True,
                'subject': True,
                'body_text_1_md': True,
            },
            "optional_fields_for_publication":
                template_config_default['optional_fields_for_publication'],
            "one_of_fields_for_publication":
                template_config_default['one_of_fields_for_publication'],
            "dependent_field_names":
                template_config_default['dependent_field_names'],
        },
    }

    subject = models.CharField(max_length=80, blank=True)
    header_image = models.ImageField(
        upload_to='header/', blank=True,
        help_text='résolution recommandée : 1600x500')

    # Content #######################################################
    body_text_1_md = models.TextField(blank=True)
    body_image_1 = models.ImageField(
        upload_to='body/', blank=True,
        help_text='résolution recommandée : 1600x500')
    body_image_1_alt_text = models.CharField(max_length=100, blank=True)

    # Plus slug, template, title, comment, and social media fields,
    # provided through abstract base class.

    new_object_url = 'topicblog:new_press'
    listone_object_url = 'topicblog:list_press_by_slug'
    listall_object_url = 'topicblog:list_press'
    viewbyslug_object_url = 'topicblog:view_press_by_slug'
    send_object_url = 'topicblog:send_press'
    description_of_object = 'Communiqué de presse'

    def get_absolute_url(self):
        """Provide a link to view this object (by slug and id).
        """
        if self.slug:
            return reverse("topicblog:view_press_by_pkid",
                           kwargs={"pkid": self.pk,
                                   "the_slug": self.slug})
        else:
            return reverse("topicblog:view_press_by_pkid_only",
                           kwargs={"pkid": self.pk})

    def get_edit_url(self):
        """Provide a link to edit this object (by slug and id).
        """
        if not self.slug:
            return reverse("topicblog:edit_press_by_pkid",
                           kwargs={"pkid": self.pk})
        else:
            return reverse("topicblog:edit_press",
                           kwargs={"pkid": self.pk,
                                   "the_slug": self.slug})

    def get_participating_field_names(self) -> set:
        """
        Return the names of fields that participate in this TopicBlogObject
        based on the Template it uses.

        This only provides user-settable fields.
        """
        fields = super().get_participating_field_names()
        template = self.template_name
        template_cfg = self.template_config[template]
        for field_name, value in template_cfg["fields"].items():
            if field_name == "subject":
                fields.add('subject')
                continue
            if field_name == "body_text_1_md":
                fields.add('body_text_1_md')
                continue
            if field_name == "body_image_1":
                fields.add('body_image_1')
                fields.add('body_image_1_alt_text')
                continue
        return fields


class SendRecordMarketingPress(SendRecordMarketing):
    """Represent the sending of a TBPress."""
    class Meta:
        constraints = [
                models.UniqueConstraint(
                    fields=['recipient', 'slug'],
                    name='TBP_unique_recipient_slug')
            ]


class TopicBlogPressClicks(models.Model):

    """Represent the fact that an press was clicked.

    Note that SendRecordMarketingPress will record the first click,
    but here we want to record all clicks that happen and where they
    lead.

    """
    press = models.ForeignKey(SendRecordMarketingPress,
                              on_delete=models.PROTECT)
    click_time = models.DateTimeField()
    click_url = models.CharField(max_length=1024, blank=False)


######################################################################
# TopicBlogLauncher
def validate_launcher_image(value):
    """
    Validates the launcher_image field.
    """
    if value is None:
        return None
    SIDE_SIZE_IN_PX = 435
    if value.width < SIDE_SIZE_IN_PX or value.height < SIDE_SIZE_IN_PX:
        raise ValidationError(
            "L'image doit avoir une largeur et une hauteur "
            f"d'au moins {SIDE_SIZE_IN_PX}px")


class TopicBlogLauncher(TopicBlogObjectBase):
    """Represent a launcher (project square, campaign entry point).

    We use this to represent panels that point to articles about
    campaigns.  We also use it for teasers to incite users to visit
    other campaigns.  The primary goal of a TBLauncher, whether
    rendered as a class square launcher or rendered as a teaser, is to
    incite the visitor to read more of our site, to click more, to
    engage more.

    """
    class Meta:
        permissions = (
            # The simpleset permission allows a user to view TBLauncher
            # that are draft or retired.
            ("tbla.may_view", "May view unpublished TopicBlogLauncher"),

            # Granting edit permission to users does not in itself
            # permit them to publish or retire, so it is reasonably
            # safe.
            ("tbla.may_edit", "May create and modify TopicBlogLauncher"),

            # Finally, we can grant users permission to publish, to
            # self-publish (implies tbla_may_publish), to send, and to
            # self-send.
            ("tbla.may_publish", "May publish TopicBlogLauncher"),
            ("tbla.may_publish_self", "May publish own TopicBlogLauncher"),
        )
    # Content Type ##################################################
    #
    # The content types match existing templates with their content type.
    # "content type": [list of templates available for this type]
    # The templates in the list must :
    # 1) Exist in the templates/ directory
    # 2) be configurated in self.template_config
    # Default values for template_config ###########################
    template_config_default = {
        "optional_fields_for_publication": (),
        # Fields that, if required for publication, the requirement is
        # satisfied by providing any one of them.
        "one_of_fields_for_publication": [],
        # Dependent fields: if one in a group is provided, the others must
        # be as well before we can publish.
        "dependent_field_names": [],
    }
    template_config = {
        'topicblog/content_launcher.html': {
            'user_template_name': 'Classic',
            'active': True,
            "fields": {
                'slug': True,
                'headline': True,
                'article_slug:': True,
                'campaign_name': True,
                'launcher_text_md:': True,
                'launcher_image': True,
                'launcher_image_alt_text': True,
            },
            "optional_fields_for_publication":
                template_config_default['optional_fields_for_publication'],
            "one_of_fields_for_publication":
                template_config_default['one_of_fields_for_publication'],
            "dependent_field_names":
                template_config_default['dependent_field_names'],
        },
    }

    headline = models.CharField(max_length=80, blank=True)
    launcher_text_md = models.TextField(blank=True)
    launcher_image = models.ImageField(
        upload_to='launcher/', blank=True,
        help_text='résolution recommandée : 667x667',
        validators=[validate_launcher_image])
    launcher_image_alt_text = models.CharField(max_length=100, blank=True)

    # The TBItem to which this slug points.
    article_slug = models.SlugField(max_length=90, allow_unicode=True,
                                    blank=True)

    # Campaign name.  This is free text.  The intent is that two
    # launchers to the same campaign may not be displayed
    # simultaneously.  Thus, it's a way of providing more than one
    # launcher to the same campaign without risk that they interfere
    # with each other.
    campaign_name = models.CharField(max_length=80, blank=True)
    # The numbers of chars that will be displayed on an item_teaser
    # templatetag
    teaser_chars = models.IntegerField(default=50, blank=False)
    # Plus slug, template, title, and comment fields, provided through
    # abstract base class.

    new_object_url = 'topicblog:new_launcher'
    listone_object_url = 'topicblog:list_launcher_by_slug'
    listall_object_url = 'topicblog:list_launcher'
    viewbyslug_object_url = 'topicblog:view_launcher_by_slug'
    description_of_object = 'Lanceur'

    def get_absolute_url(self):
        """Provide a link to view this object (by slug and id).
        """
        if self.slug:
            return reverse("topicblog:view_launcher_by_pkid",
                           kwargs={"pkid": self.pk,
                                   "the_slug": self.slug})
        else:
            return reverse("topicblog:view_launcher_by_pkid_only",
                           kwargs={"pkid": self.pk})

    def get_edit_url(self):
        """Provide a link to edit this object (by slug and id).
        """
        if not self.slug:
            return reverse("topicblog:edit_launcher_by_pkid",
                           kwargs={"pkid": self.pk})
        else:
            return reverse("topicblog:edit_launcher",
                           kwargs={"pkid": self.pk,
                                   "the_slug": self.slug})

    def set_social_context(self, context):
        """We don't need this function here, but I don't see (today) an easy
        way to avoid it getting called from the base view without a
        rather extensive refactor.

        """
        return context

    def __str__(self):
        return f"{self.headline} - ID : {self.pk}"


class TopicBlogMailingListPitch(TopicBlogObjectSocialBase):
    """Represent a mailing list signup page.

    A TBMLP displays as a web page like a TBItem but also encapsulates
    the mailing list whose membership we are pitching, the web page to
    display on signup, and the email to send on signup.

    """
    class Meta:
        verbose_name_plural = "Mailing list pitches"
        permissions = (
            ("tbmlp.may_view",
             "May view unpublished TopicBlogMailingListPitch"),
            ("tbmlp.may_edit",
             "May create and modify TopicBlogMailingListPitch"),
            ("tbmlp.may_publish",
             "May publish TopicBlogMailingListPitch"),
            ("tbmlp.may_publish_self",
             "May publish own TopicBlogMailingListPitch"),
        )

    body_text_1_md = models.TextField(blank=True)
    cta_1_slug = models.SlugField(max_length=90, allow_unicode=True,
                                  blank=True)
    cta_1_label = models.CharField(max_length=80, blank=True)
    mailing_list = models.ForeignKey('mailing_list.MailingList',
                                     on_delete=models.PROTECT)
    subscription_form_title = models.CharField(max_length=80, blank=True)
    subscription_form_button_label = models.CharField(max_length=80,
                                                      blank=True)

    template_config_default = {
        "optional_fields_for_publication": (
            'header_title',
            'header_image', 'header_description',
            'cta_1_slug', 'cta_1_label',
            'twitter_title', 'twitter_description',
            'twitter_image', 'og_title',
            'og_description', 'og_image',
        ),
        "one_of_fields_for_publication": [
            ['header_title', 'header_description'],
        ],
        # Dependent fields: if one in a group is provided, the others must
        # be as well before we can publish.
        "dependent_field_names": [
            ['cta_1_slug', 'cta_1_label'],
        ],
    }
    template_config = {
        'topicblog/content_mlp.html': {
            'user_template_name': 'Classique',
            'active': True,
            "fields": {
                'slug': True,
                'title': True,
                'header': True,
                'body_text_1_md': True,
                'cta_1_slug:': True,
                'cta_1_label': True,
                'mailing_list:': True,
                'social_media': True,
            },
            "optional_fields_for_publication":
                template_config_default['optional_fields_for_publication'],
            "one_of_fields_for_publication":
                template_config_default['one_of_fields_for_publication'],
            "dependent_field_names":
                template_config_default['dependent_field_names'],
        },
    }

    new_object_url = 'topicblog:new_mlp'
    listone_object_url = 'topicblog:list_mlp_by_slug'
    listall_object_url = 'topicblog:list_mlp'
    viewbyslug_object_url = 'topicblog:view_mlp_by_slug'
    viewbyid_object_url = 'topicblog:view_mlp_by_pkid'
    description_of_object = 'Pitch de mailing list'

    def get_absolute_url(self):
        """Provide a link to view this object (by slug and id).
        """
        if self.slug:
            return reverse("topicblog:view_mlp_by_pkid",
                           kwargs={"pkid": self.pk,
                                   "the_slug": self.slug})
        else:
            return reverse("topicblog:view_mlp_by_pkid_only",
                           kwargs={"pkid": self.pk})

    def get_edit_url(self):
        """Provide a link to edit this object (by slug and id).
        """
        if not self.slug:
            return reverse("topicblog:edit_mlp_by_pkid",
                           kwargs={"pkid": self.pk})
        else:
            return reverse("topicblog:edit_mlp",
                           kwargs={"pkid": self.pk,
                                   "the_slug": self.slug})
