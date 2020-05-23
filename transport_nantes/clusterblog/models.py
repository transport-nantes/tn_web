from django.db import models

"""
A ClusterBlog is a set of pages with short content that link randomly
to other content within the same cluster.

"""

class ClusterBlog(models.Model):
    """Represent a cluster.
    
    Random links will stay within a cluster.
    """
    blog_name = models.CharField(max_length=80, blank=False)
    # More information about the survey.  For humans.
    description = models.TextField()
    # The name of the template that we use to display the blog entries for this cluster.
    template_name = models.CharField(max_length=80, blank=False)

    def __str__(self):
        return self.blog_name

class ClusterBlogCategory(models.Model):
    """The categories associated with a ClusterBlog instance.
    """
    cluster = models.ForeignKey(ClusterBlog, on_delete=models.CASCADE)
    category = models.CharField(max_length=40, blank=False)
    # Until we have several entries in a category, we assuredly don't
    # want the next button to stick to the one category.  The user
    # would just see it sticking to one category or oscilating between
    # a couple.
    random_entries_stick_to_category = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return '{cl}/{cat}'.format(cl=self.cluster, cat=self.category)

class ClusterBlogEntry(models.Model):
    """Represent articles within a cluster.

    Random links stay within the cluster.
    They may be restricted by category.
    """
    cluster = models.ForeignKey(ClusterBlog, on_delete=models.CASCADE)
    slug =  models.CharField(max_length=80, blank=False, unique=True)
    category = models.ForeignKey(ClusterBlogCategory, on_delete=models.PROTECT)
    title = models.CharField(max_length=80, blank=False)
    description = models.TextField()
    image_filename = models.CharField(max_length=80, blank=False)
    approved = models.BooleanField(default=False)

    og_title = models.CharField(max_length=80, blank=True)
    og_description = models.TextField()
    og_image = models.CharField(max_length=80, blank=True)
    og_image_alt = models.TextField(blank=True)
    og_image_type = models.CharField(max_length=40, blank=True)

    class Meta:
        verbose_name_plural = "ClusterBlogEntries"

    def __str__(self):
        if self.approved:
            approved='+'
        else:
            approved='-'
        return '{appr}{cl} | {cat} | {sl} / {tit}'.format(
            appr=approved,
            cl=self.cluster.blog_name,
            cat=self.category.category,
            sl=self.slug, tit=self.title)

    def random_entry(cluster_id, category_id):
        """Select a random entry associated with the given cluster and
        category.

        This would be quite inefficient if we had an enormous number
        of entries in a single category.  As it happens, we don't
        think that will be the case.  Meanwhile, classical solutions
        of finding (aggregate) the max index, then picking a not
        greater positive int at random with retry if the select fails
        would be quite bad here, since we'd have more misses than hits.

        """
        category = ClusterBlogCategory.objects.get(id=category_id)
        if category.random_entries_stick_to_category:
            entry = ClusterBlogEntry.objects.filter(
                cluster=cluster_id, category=category_id, approved=True).order_by('?').first()
            return entry
        entry = ClusterBlogEntry.objects.filter(
            cluster=cluster_id, approved=True).order_by('?').first()
        return entry
