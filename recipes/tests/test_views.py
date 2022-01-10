import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from recipes.factories import RecipeFactory, ShareConfigFactory
from recipes.models import Recipe
from users.models import User


class BaseRecipesTestCase(APITestCase):
    def setUp(self) -> None:
        self.user1 = User.objects.create(email='user1@test.com', username='user1@test.com')
        self.user2 = User.objects.create(email='user2@test.com', username='user2@test.com')
        self.client.force_authenticate(self.user1)


class RecipeListTestCase(BaseRecipesTestCase):
    def test_user_sees_their_recipes(self):
        r1 = RecipeFactory(author=self.user1, name='test recipe 1')
        r2 = RecipeFactory(author=self.user1, name='test recipe 2')
        r3 = RecipeFactory(author=self.user1, name='test recipe 2')

        url = reverse('recipes-list')
        resp = self.client.get(url)
        json_content = json.loads(resp.content)
        fetched_recipe_names = [r['name'] for r in json_content]
        expected_recipe_names = [r3.name, r1.name, r2.name]

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json_content), 3)
        self.assertCountEqual(fetched_recipe_names, expected_recipe_names)

    def test_user_sees_recipes_shared_with_them(self):
        user1_recipe = RecipeFactory(author=self.user1, name="user1's recipe")
        user2_recipe = RecipeFactory(author=self.user2, name="user2's recipe")
        ShareConfigFactory(granter=self.user2, grantee=self.user1)

        url = reverse('recipes-list')
        resp = self.client.get(url)
        json_content = json.loads(resp.content)
        fetched_recipe_names = [r['name'] for r in json_content]
        expected_recipe_names = [user2_recipe.name, user1_recipe.name]

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json_content), 2)
        self.assertCountEqual(fetched_recipe_names, expected_recipe_names)

    def test_user_does_not_see_recipes_they_dont_own_or_have_access_to(self):
        user1_recipe = RecipeFactory(author=self.user1, name="user1's recipe")
        RecipeFactory(author=self.user2, name="user2's recipe")

        url = reverse('recipes-list')
        resp = self.client.get(url)
        json_content = json.loads(resp.content)
        fetched_recipe_names = [r['name'] for r in json_content]
        expected_recipe_names = [user1_recipe.name]

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json_content), 1)
        self.assertCountEqual(fetched_recipe_names, expected_recipe_names)

    def test_recipes_filtered_by_tag(self):
        r1 = RecipeFactory(author=self.user1, name='Red lentils', tags=['indian', 'lentils'])
        r2 = RecipeFactory(author=self.user1, name='Chana masala', tags=['indian'])
        r3 = RecipeFactory(author=self.user1, name='Kung Pao Chicken', tags=['chinese'])
        RecipeFactory(author=self.user1, name='Pizza', tags=['italian'])

        url = reverse('recipes-list')
        resp = self.client.get(f'{url}?tags=indian,chinese')
        json_content = json.loads(resp.content)
        recipe_names = [r['name'] for r in json_content]
        expected_names = [r1.name, r2.name, r3.name]

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json_content), 3)
        self.assertCountEqual(recipe_names, expected_names)

    def test_recipes_filtered_by_tag_no_results(self):
        RecipeFactory(author=self.user1, name='Red lentils', tags=['indian', 'lentils'])
        RecipeFactory(author=self.user1, name='Chana masala', tags=['indian'])
        RecipeFactory(author=self.user1, name='Kung Pao Chicken', tags=['chinese'])

        url = reverse('recipes-list')
        resp = self.client.get(f'{url}?tags=bad-tag')
        json_content = json.loads(resp.content)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json_content), 0)


class RecipeCreateTestCase(BaseRecipesTestCase):
    def test_create_recipe_with_required_fields(self):
        url = reverse('recipes-list')
        data = {
            "name": "test recipe",
        }

        resp = self.client.post(url, data, format='json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Recipe.objects.count(), 1)
        self.assertEqual(Recipe.objects.get().name, 'test recipe')

    def test_create_recipe_raises_400_if_missing_required_data(self):
        url = reverse('recipes-list')
        data = {}

        resp = self.client.post(url, data, format='json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class RecipeDetailsTestCase(BaseRecipesTestCase):
    def test_get_by_pk(self):
        recipe = RecipeFactory(author=self.user1)

        url = reverse('recipes-detail', kwargs={'pk': recipe.pk})
        resp = self.client.get(url)
        json_content = json.loads(resp.content)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(json_content['name'], recipe.name)

    def test_user_gets_404_when_trying_to_get_recipe_they_dont_have_access_to(self):
        recipe = RecipeFactory(author=self.user2, name="user2's recipe")

        url = reverse('recipes-detail', kwargs={'pk': recipe.pk})
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_by_public_id_and_slug(self):
        recipe = RecipeFactory(author=self.user1)

        url = reverse('recipes-detail', kwargs={'pk': f'{recipe.public_id}-{recipe.slug}'})
        resp = self.client.get(url)
        json_content = json.loads(resp.content)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(json_content['name'], recipe.name)


class RecipeUpdateTestCase(BaseRecipesTestCase):
    def test_user_can_update_a_recipe_they_own(self):
        recipe = RecipeFactory(author=self.user1, name='original name')

        url = reverse('recipes-detail', kwargs={'pk': recipe.pk})
        resp = self.client.patch(url, data={'name': 'updated name'}, format='json')
        json_content = json.loads(resp.content)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(json_content['name'], 'updated name')
        self.assertEqual(
            Recipe.objects.get(pk=recipe.id).name,
            'updated name'
        )

    def test_user_can_update_a_recipe_that_was_shared_with_them(self):
        recipe = RecipeFactory(author=self.user2, name='original name')
        ShareConfigFactory(granter=self.user2, grantee=self.user1)

        url = reverse('recipes-detail', kwargs={'pk': recipe.pk})
        resp = self.client.patch(url, data={'name': 'updated name'}, format='json')
        json_content = json.loads(resp.content)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(json_content['name'], 'updated name')
        self.assertEqual(
            Recipe.objects.get(pk=recipe.id).name,
            'updated name'
        )

    def test_user_gets_404_when_trying_to_update_recipe_they_dont_have_access_to(self):
        recipe = RecipeFactory(author=self.user2, name='original name')

        url = reverse('recipes-detail', kwargs={'pk': recipe.pk})
        resp = self.client.patch(url, data={'name': 'updated name'}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


class RecipeDeleteTestCase(BaseRecipesTestCase):
    def test_user_can_delete_a_recipe_they_own(self):
        recipe = RecipeFactory(author=self.user1, name='original name')

        url = reverse('recipes-detail', kwargs={'pk': recipe.pk})
        resp = self.client.delete(url, data={'name': 'updated name'}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(pk=recipe.id).exists())

    def test_user_can_delete_a_recipe_that_was_shared_with_them(self):
        recipe = RecipeFactory(author=self.user2, name='original name')
        ShareConfigFactory(granter=self.user2, grantee=self.user1)

        url = reverse('recipes-detail', kwargs={'pk': recipe.pk})
        resp = self.client.delete(url)

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(pk=recipe.id).exists())

    def test_user_gets_404_when_trying_to_delete_recipe_they_dont_have_access_to(self):
        recipe = RecipeFactory(author=self.user2, name='original name')

        url = reverse('recipes-detail', kwargs={'pk': recipe.pk})
        resp = self.client.delete(url)

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
