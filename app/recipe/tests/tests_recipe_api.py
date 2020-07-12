from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

# recipe: app-name
# recipe-list: identifier of url in the app, listing api for the recipe
# NOTE: no space in between app and listing api
RECIPES_URL = reverse('recipe:recipe-list')


# require argument in url
# /api/recipe/recipes/
# /api/recipe/recipes/1/

def detail_url(recipe_id):
    """Return recipe detail url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='Main Course'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Cinnamon'):
    """"Create and return a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


# helper fn called sample recipe, to easily create sample recipes for us to
# play in the test
# ** any additional will be passed to a dict called params
def sample_recipe(user, **params):
    """Create and return a sample recipe"""

    # new concept to create helper fns when we need repeated objects in our
    # test
    # user already passed in args, so no need to pass in defaults
    # **params will convert arguments into dict
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    # update fn that comes with python dictionary
    # it accepts a dict object and take keys in dict and update them
    # if keys doesnt exist, it will create them
    defaults.update(params)

    # **defaults will convert dict into arguments
    # reverse effect to **params
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated recipe API access"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authenticated is required"""
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated recipe API access"""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'testuser@kazang.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test retrieving recipes for user"""
        user2 = get_user_model().objects.create_user(
            'other@kazang.com',
            'otherpwd'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)
