from django.contrib import admin

from .models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredientLink,
    ShoppingListEntry,
)


@admin.register(Ingredient)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "measurement_unit")
    search_fields = ("name",)
    list_filter = ("measurement_unit",)
    empty_value_display = "-пусто-"


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredientLink
    extra = 1
    min_num = 1
    autocomplete_fields = ("ingredient",)


@admin.register(Recipe)
class DishAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "author", "cooking_time", "pub_date",
                    "favorite_count")
    search_fields = ("name", "author__username")
    list_filter = ("author", "name", "pub_date")
    readonly_fields = ("pub_date", "favorite_count")
    inlines = (RecipeIngredientInline,)
    empty_value_display = "-пусто-"

    @admin.display(description="Количество в избранном")
    def favorite_count(self, obj):
        return obj.favorited_by.count()

    favorite_count.short_description = "Количество в избранном"


@admin.register(RecipeIngredientLink)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "recipe", "ingredient", "amount")
    search_fields = ("recipe__name", "ingredient__name")
    autocomplete_fields = ("recipe", "ingredient")


@admin.register(FavoriteRecipe)
class UserFavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe", "added_at")
    search_fields = ("user__username", "recipe__name")
    list_filter = ("added_at",)
    autocomplete_fields = ("user", "recipe")


@admin.register(ShoppingListEntry)
class UserShoppingListAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe", "added_at")
    search_fields = ("user__username", "recipe__name")
    list_filter = ("added_at",)
    autocomplete_fields = ("user", "recipe")
