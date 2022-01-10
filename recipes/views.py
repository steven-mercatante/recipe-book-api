from uuid import UUID
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.generics import ListAPIView

from .models import Recipe, RecipeTag
from .serializers import RecipeSerializer, RecipeTagSerializer


class RecipeTagView(ListAPIView):
    """
    Fetch all RecipeTags for Recipes that the current user
    has access to.
    """
    serializer_class = RecipeTagSerializer

    def get_queryset(self):
        recipe_ids = self.request.user.get_recipe_ids()
        return RecipeTag.objects.filter(
            recipe__id__in=recipe_ids
        )


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer

    def get_queryset(self):
        # Start by building a queryset for all Recipes the user has access to,
        # including Recipes that've been shared.
        recipe_ids = self.request.user.get_recipe_ids()
        queryset = Recipe.objects.filter(pk__in=recipe_ids)

        # Filter by tag slugs if `tags` query param is present
        try:
            tags = self.request.query_params.get('tags').split(',')
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        except AttributeError:
            pass

        return queryset

    # TODO: test fetch by pk and composite (public_id, slug)
    def retrieve(self, request, *args, **kwargs):
        try:
            # If kwargs['pk'] is not a valid UUID, an error is raised,
            # and you can assume you need to look the recipe up by
            # the composite (public_id, slug)
            UUID(kwargs['pk'])
            recipe = get_object_or_404(Recipe, pk=kwargs['pk'])
        except ValueError as e:
            # We used a combination of the recipe's public_id and slug
            # for shareable links, rather than the recipe's UUID.
            # maxsplit=1 is needed because the slug can have more than
            # one hyphen in it.
            [public_id, slug] = kwargs['pk'].split('-', maxsplit=1)
            recipe = get_object_or_404(Recipe, public_id=public_id, slug=slug)

        serializer = RecipeSerializer(recipe)
        return Response(serializer.data)
