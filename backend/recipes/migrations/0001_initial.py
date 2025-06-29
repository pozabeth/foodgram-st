# Generated by Django 5.2 on 2025-05-29 15:01

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Введите название используемого продукта', max_length=128, verbose_name='Наименование ингредиента')),
                ('measurement_unit', models.CharField(help_text='Укажите единицу измерения (например, грамм или штука)', max_length=64, verbose_name='Мера измерения')),
            ],
            options={
                'verbose_name': 'Продукт',
                'verbose_name_plural': 'Продукты',
                'ordering': ['name'],
                'constraints': [models.UniqueConstraint(fields=('name', 'measurement_unit'), name='unique_ingredient_unit')],
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Введите заголовок для вашего рецепта', max_length=256, verbose_name='Заголовок рецепта')),
                ('image', models.ImageField(help_text='Добавьте визуальное представление рецепта', upload_to='recipes/images/', verbose_name='Фото рецепта')),
                ('text', models.TextField(help_text='Опишите шаги приготовления и состав', verbose_name='Текстовое описание рецепта')),
                ('cooking_time', models.PositiveSmallIntegerField(help_text='Укажите время, необходимое для готовки', validators=[django.core.validators.MinValueValidator(1, message='Минимальное время — 1 минута'), django.core.validators.MaxValueValidator(32000, message='Слишком большое значение')], verbose_name='Длительность приготовления (минуты)')),
                ('pub_date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата добавления')),
                ('author', models.ForeignKey(help_text='Пользователь, который добавил рецепт', on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Создатель рецепта')),
            ],
            options={
                'verbose_name': 'Кулинарный рецепт',
                'verbose_name_plural': 'Кулинарные рецепты',
                'ordering': ['-pub_date'],
            },
        ),
        migrations.CreateModel(
            name='RecipeIngredientLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(help_text='Укажите объём или вес ингредиента', validators=[django.core.validators.MinValueValidator(1, message='Минимальное количество — 1'), django.core.validators.MaxValueValidator(32000, message='Чрезмерно много')], verbose_name='Объем или масса')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredients', to='recipes.ingredient', verbose_name='Продукт')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredients', to='recipes.recipe', verbose_name='Блюдо')),
            ],
            options={
                'verbose_name': 'Ингредиент для рецепта',
                'verbose_name_plural': 'Ингредиенты для рецептов',
            },
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(help_text='Выберите необходимые компоненты для этого рецепта', related_name='recipes', through='recipes.RecipeIngredientLink', to='recipes.ingredient', verbose_name='Список продуктов'),
        ),
        migrations.CreateModel(
            name='ShoppingListEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='in_shopping_cart_of', to='recipes.recipe', verbose_name='Нужный к покупке рецепт')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_cart', to=settings.AUTH_USER_MODEL, verbose_name='Владелец списка')),
            ],
            options={
                'verbose_name': 'Элемент списка покупок',
                'verbose_name_plural': 'Списки покупок',
                'ordering': ['-added_at'],
            },
        ),
        migrations.CreateModel(
            name='FavoriteRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorited_by', to='recipes.recipe', verbose_name='Рецепт в закладках')),
            ],
            options={
                'verbose_name': 'Любимый рецепт',
                'verbose_name_plural': 'Любимые рецепты',
                'ordering': ['-added_at'],
                'constraints': [models.UniqueConstraint(fields=('user', 'recipe'), name='unique_user_favorite_recipe')],
            },
        ),
        migrations.AddConstraint(
            model_name='recipeingredientlink',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredient'), name='unique_recipe_ingredient'),
        ),
        migrations.AddConstraint(
            model_name='shoppinglistentry',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_user_shopping_cart_recipe'),
        ),
    ]
