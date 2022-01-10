from factory.django import DjangoModelFactory

from . import models


class RecipeFactory(DjangoModelFactory):
    class Meta:
        model = models.Recipe

    name = "factory made recipe"
