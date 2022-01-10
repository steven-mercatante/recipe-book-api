import factory
from factory.django import DjangoModelFactory

from . import models


class RecipeFactory(DjangoModelFactory):
    name = "factory made recipe"

    class Meta:
        model = models.Recipe

    # Extra work is needed to play nicely with django-taggit
    # See: https://stackoverflow.com/a/43253817/155175
    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for tag in extracted:
                self.tags.add(tag)


class ShareConfigFactory(DjangoModelFactory):
    class Meta:
        model = models.ShareConfig
