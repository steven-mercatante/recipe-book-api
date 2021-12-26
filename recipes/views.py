from rest_framework import viewsets

from .models import Recipe
from .serializers import RecipeSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    # TODO: restrict to user
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
