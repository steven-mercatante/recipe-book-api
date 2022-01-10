from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer

from .models import Recipe, RecipeTag


class RecipeSerializer(TaggitSerializer, serializers.ModelSerializer):
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    tags = TagListSerializerField()

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
            'tags',
            'total_time',
            'video_url',
        ]
        read_only_fields = [
            'id',
            'public_id',
            'slug',
        ]


class RecipeTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeTag
        fields = ['name', 'slug']
