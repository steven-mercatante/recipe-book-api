from rest_framework import serializers

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
            'video_url',
        ]

    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
