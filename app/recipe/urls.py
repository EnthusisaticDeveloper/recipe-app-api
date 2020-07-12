from django.urls import path, include
from rest_framework.routers import DefaultRouter
from recipe import views

# default router is a feature of DRF that will automatically generate URLS for
# our viewset

# api/recipe/tags
# api/recipe/tags/id

# Default router automatically registers the appropriate URLs for all of the
# actions in our viewset

router = DefaultRouter()
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)
router.register('recipes', views.RecipeViewSet)

# this registers our viewset with our router

app_name = 'recipe'  # for reverse function to lookup correct URLs

urlpatterns = [
    path('', include(router.urls)),
]
