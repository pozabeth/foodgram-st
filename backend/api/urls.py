from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CustomUserManagerViewSet,
    IngredientViewSet,
    RecipeManagerViewSet,
)

router = DefaultRouter()

router.register("users", CustomUserManagerViewSet, basename="users")

router.register("ingredients", IngredientViewSet, basename="ingredients")

router.register("recipes", RecipeManagerViewSet, basename="recipes")


urlpatterns = [
    path("", include(router.urls)),
]
