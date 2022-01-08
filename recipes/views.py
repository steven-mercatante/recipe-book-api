from uuid import UUID
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response

from .models import Recipe
from .serializers import RecipeSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer

    def get_queryset(self):
        return Recipe.objects.filter(author=self.request.user)

    # TODO: test fetch by pk and composite (public_id, slug)
    def retrieve(self, request, *args, **kwargs):
        try:
            # If kwargs['pk'] is not a valid UUID, an error is raised
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
