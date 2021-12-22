# This script initializes the database with a single topicblog item
# that should allow a new user to see the index page at /.
from datetime import datetime, timezone

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.contrib.auth.models import User

from topicblog.models import (TopicBlogItem,
                              TopicBlogContentType,
                              TopicBlogTemplate)


class Command(BaseCommand):
    help = 'Initialize the database with a single topicblog item'

    def handle(self, *args, **options):
        try:
            # Migrates the database first
            call_command("migrate", interactive=False)
        except CommandError as e:
            self.stdout.write(e)
            self.stdout.write("Migration failed. Aborting.")
            exit(1)

        try:
            superuser = User.objects.create_superuser(username='Superuser',
                                                      password='admin')

            article = TopicBlogContentType.objects.create(
                content_type="article",
            )

            default_template = TopicBlogTemplate.objects.create(
                template_name="topicblog/content.html",
                comment="Default template for topicblog items",
                content_type=article,
                slug=True,
                title=True,
            )

            index_page = TopicBlogItem.objects.create( # noqa
                slug="index",
                item_sort_key=0,
                user=superuser,
                content_type=article,
                template=default_template,
                title="Mobilitains - Pour une mobilité multimodale",
                servable=True,
                publication_date=datetime.now(timezone.utc),
            )
        except CommandError as e:
            self.stdout.write(e)

        self.stdout.write(self.style.SUCCESS(
            'Successfully initialized the database !'))
