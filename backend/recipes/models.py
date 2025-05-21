from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

MIN_INGREDIENT_AMOUNT = 1
MAX_INGREDIENT_AMOUNT = 32000
MIN_COOKING_TIME = 1
MAX_COOKING_TIME = 32000


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name="Наименование ингредиента",
        max_length=128,
        help_text="Введите название используемого продукта",
    )
    measurement_unit = models.CharField(
        verbose_name="Мера измерения",
        max_length=64,
        help_text="Укажите единицу измерения (например, грамм или штука)",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="unique_ingredient_unit"
            )
        ]

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"


class Recipe(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Создатель рецепта",
        help_text="Пользователь, который добавил рецепт",
    )
    name = models.CharField(
        verbose_name="Заголовок рецепта",
        max_length=256,
        help_text="Введите заголовок для вашего рецепта",
    )
    image = models.ImageField(
        verbose_name="Фото рецепта",
        upload_to="recipes/images/",
        help_text="Добавьте визуальное представление рецепта",
    )
    text = models.TextField(
        verbose_name="Текстовое описание рецепта",
        help_text="Опишите шаги приготовления и состав",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredientLink",
        related_name="recipes",
        verbose_name="Список продуктов",
        help_text="Выберите необходимые компоненты для этого рецепта",
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Длительность приготовления (минуты)",
        validators=[
            MinValueValidator(1, message="Минимальное время — 1 минута"),
            MaxValueValidator(32000, message="Слишком большое значение"),
        ],
        help_text="Укажите время, необходимое для готовки",
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата добавления", auto_now_add=True, db_index=True
    )

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "Кулинарный рецепт"
        verbose_name_plural = "Кулинарные рецепты"

    def __str__(self):
        return f"{self.name} (автор: {self.author.username})"


class RecipeIngredientLink(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Блюдо",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Продукт",
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Объем или масса",
        validators=[
            MinValueValidator(1, message="Минимальное количество — 1"),
            MaxValueValidator(32000, message="Чрезмерно много"),
        ],
        help_text="Укажите объём или вес ингредиента",
    )

    class Meta:
        verbose_name = "Ингредиент для рецепта"
        verbose_name_plural = "Ингредиенты для рецептов"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_recipe_ingredient"
            )
        ]

    def __str__(self):
        return (
            f"{self.ingredient.name} ({self.amount} "
            f'{self.ingredient.measurement_unit}) в "{self.recipe.name}"'
        )


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name="Рецепт в закладках",
    )
    added_at = models.DateTimeField(verbose_name="Дата добавления",
                                    auto_now_add=True)

    class Meta:
        ordering = ["-added_at"]
        verbose_name = "Любимый рецепт"
        verbose_name_plural = "Любимые рецепты"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_user_favorite_recipe"
            )
        ]

    def __str__(self):
        return f'"{self.recipe.name}" в закладках у {self.user.username}'


class ShoppingListEntry(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Владелец списка",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="in_shopping_cart_of",
        verbose_name="Нужный к покупке рецепт",
    )
    added_at = models.DateTimeField(verbose_name="Дата добавления",
                                    auto_now_add=True)

    class Meta:
        ordering = ["-added_at"]
        verbose_name = "Элемент списка покупок"
        verbose_name_plural = "Списки покупок"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_user_shopping_cart_recipe"
            )
        ]

    def __str__(self):
        return f'"{self.recipe.name}" в списке покупок у {self.user.username}'
