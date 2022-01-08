import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify


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

    @property
    def public_id(self):
        return str(self.id)[:8]

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Recipe, self).save(*args, **kwargs)
