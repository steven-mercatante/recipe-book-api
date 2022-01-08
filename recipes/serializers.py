from rest_framework import serializers

from .models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = [
            'id',
            'active_time',
            'author',
            'name',
            'ingredients',
            'instructions',
            'public_id',
            'notes',
            'slug',
            'source',
            'total_time',
            'video_url',
        ]
        read_only_fields = [
            'id',
            'public_id',
            'slug',
        ]

    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
