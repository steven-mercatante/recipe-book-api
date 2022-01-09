import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify
from taggit.managers import TaggableManager
from taggit.models import GenericUUIDTaggedItemBase, TagBase, TaggedItemBase


# We need to define custom `RecipeTag` and `TaggedRecipe` models because
# `Recipe` uses a UUID for its ID, and taggit only supports integer IDs
# out of the box.
# See: https://django-taggit.readthedocs.io/en/latest/custom_tagging.html#genericuuidtaggeditembase
class RecipeTag(TagBase):
    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"


class TaggedRecipe(GenericUUIDTaggedItemBase, TaggedItemBase):
    tag = models.ForeignKey(
        RecipeTag,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_items",
    )


class Recipe(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(blank=True, max_length=75)
    ingredients = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    video_url = models.CharField(blank=True, max_length=255)
    source = models.CharField(max_length=255, blank=True)
    active_time = models.CharField(max_length=25, blank=True)
    total_time = models.CharField(max_length=25, blank=True)
    servings = models.CharField(max_length=25, blank=True)
    # Even though public_id is derived from self.id, it's a real field
    # instead of a @property so we can use it in DB lookups.
    public_id = models.CharField(max_length=8, blank=True)
    tags = TaggableManager(through=TaggedRecipe)

    class Meta:
        indexes = [
            models.Index(fields=['public_id', 'slug']),
        ]

    def save(self, *args, **kwargs):
        self.public_id = str(self.id)[:8]
        self.slug = slugify(self.name)
        super(Recipe, self).save(*args, **kwargs)


class ShareConfig(models.Model):
    """
    Allows sharing recipes between users.
    """
    EDITOR = 'Editor'
    VIEWER = 'Viewer'
    ROLE_CHOICES = [
        (EDITOR, EDITOR),
        (VIEWER, VIEWER),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    granter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='granter',
    )
    grantee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='grantee',
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=EDITOR)
