import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
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
    slug = models.SlugField(blank=True, max_length=75, db_index=True)
    ingredients = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    video_url = models.CharField(blank=True, max_length=255)
    source = models.CharField(max_length=255, blank=True)
    active_time = models.CharField(max_length=25, blank=True)
    total_time = models.CharField(max_length=25, blank=True)
    servings = models.CharField(max_length=25, blank=True)
    tags = TaggableManager(blank=True, through=TaggedRecipe)

    def save(self, *args, **kwargs):
        # TODO: test slug is set correctly
        self.slug = f'{str(self.id)[:8]}-{slugify(self.name)}'
        super(Recipe, self).save(*args, **kwargs)

    @staticmethod
    def copy_for_user(recipe_id, user_id):
        # TODO: might want to also copy over recipe.tags
        recipe = Recipe.objects.get(pk=recipe_id)
        user = get_user_model().objects.get(pk=user_id)

        # Copy the model instance
        # See: https://docs.djangoproject.com/en/4.0/topics/db/queries/#copying-model-instances
        recipe.pk = uuid.uuid4()
        recipe.author = user
        recipe._state.adding = True
        recipe.save()
        return recipe


    @staticmethod
    def can_user_edit_recipe(recipe_id, user_id):
        recipe_author_id = Recipe.objects.filter(
            slug=recipe_id
        ).values_list('author_id', flat=True).get()

        if recipe_author_id == user_id:
            return True

        return ShareConfig.sharing_exists(recipe_author_id, user_id)

    def __str__(self):
        return f'Recipe <{self.name}>'


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

    @staticmethod
    def sharing_exists(user_1_id, user_2_id):
        """
        Check if user_1 has access to user_2's recipes, and vice versa.
        """
        return ShareConfig.objects.filter(
            (models.Q(granter_id=user_1_id) & models.Q(grantee_id=user_2_id))
            | (models.Q(granter_id=user_2_id) & models.Q(grantee_id=user_1_id))
        ).exists()
