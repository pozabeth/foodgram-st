from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe


class IngredientSearchFilter(filters.FilterSet):
    name = filters.CharFilter(
        field_name="name",
        lookup_expr="startswith"
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeCustomFilter(filters.FilterSet):
    author = filters.NumberFilter(field_name="author__id")
    is_favorited = filters.BooleanFilter(method="apply_favorite_filter")
    is_in_shopping_cart = filters.BooleanFilter(
        method="apply_shopping_cart_filter"
    )

    class Meta:
        model = Recipe
        fields = ("author", "is_favorited", "is_in_shopping_cart")

    def apply_favorite_filter(self, queryset, name, value):
        return self._filter_queryset(queryset, value, "favorited_by__user")

    def apply_shopping_cart_filter(self, queryset, name, value):
        return self._filter_queryset(queryset, value,
                                     "in_shopping_cart_of__user")

    def _filter_queryset(self, queryset, value, relation_field):
        user = self.request.user
        if not user.is_authenticated or not value:
            return queryset.none() if value else queryset
        return queryset.filter(**{relation_field: user})
