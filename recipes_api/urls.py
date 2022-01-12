"""recipes_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
# from rest_framework.schemas import get_schema_view

from recipes import views as recipe_views

router = routers.DefaultRouter()
router.register(r'recipes', recipe_views.RecipeViewSet, basename='recipes')

urlpatterns = [
    path(
        'recipes/<str:slug>/',
        recipe_views.RecipeRetrieveView.as_view(),
        name='recipe-retrieve'
    ),
    path('', include(router.urls)),
    path(
        'recipe-tags/',
        recipe_views.RecipeTagView.as_view(),
        name='recipe-tags'
    ),
    # path('openapi', get_schema_view(
    #     title='Recipe Book',
    #     description='API for Recipe Book',
    #     version='0.3.1'
    # ), name='openapi-schema'),
    path('admin/', admin.site.urls),
]
