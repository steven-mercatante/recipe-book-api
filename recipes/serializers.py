from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer

from .models import Recipe, RecipeTag


class RecipeSerializer(TaggitSerializer, serializers.ModelSerializer):
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    owner = serializers.SerializerMethodField()
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Recipe
        fields = [
            'id',
            'active_time',
            'author',
            'name',
            'ingredients',
            'instructions',
            'notes',
            'owner',
            'slug',
            'source',
            'tags',
            'total_time',
            'video_url',
        ]
        read_only_fields = [
            'id',
            'slug',
        ]

    def get_owner(self, obj):
        return obj.author.email


class RecipeTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeTag
        fields = ['name', 'slug']
