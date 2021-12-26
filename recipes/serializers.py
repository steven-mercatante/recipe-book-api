from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from .models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = [
            'id',
            'author',
            'name',
            'ingredients',
            'instructions',
        ]

    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
