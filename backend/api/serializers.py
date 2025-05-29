from django.db import transaction
from django.http import Http404
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    MAX_COOKING_TIME,
    MAX_INGREDIENT_AMOUNT,
    MIN_COOKING_TIME,
    MIN_INGREDIENT_AMOUNT,
    Ingredient,
    Recipe,
    RecipeIngredientLink,
)
from users.models import User, UserSubscription


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")
        read_only_fields = fields


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField(read_only=True)

    class Meta(DjoserUserSerializer.Meta):
        model = User
        fields = DjoserUserSerializer.Meta.fields + ("is_subscribed", "avatar")

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return request.user.following.filter(author=obj).exists()


class RecipeIngredientOutputSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit")

    class Meta:
        model = RecipeIngredientLink
        fields = ("id", "name", "measurement_unit", "amount")


class IngredientInputSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        min_value=MIN_INGREDIENT_AMOUNT,
        max_value=MAX_INGREDIENT_AMOUNT,
        error_messages={
            "min_value": f"Минимум {MIN_INGREDIENT_AMOUNT} единиц.",
            "max_value": f"Не больше {MAX_INGREDIENT_AMOUNT} единиц.",
        },
    )


class RecipeDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientOutputSerializer(
        many=True, read_only=True, source="recipe_ingredients"
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        user = self.context["request"].user
        if not user.is_authenticated:
            return False
        return obj.favorited_by.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context["request"].user
        if not user.is_authenticated:
            return False
        return obj.in_shopping_cart_of.filter(user=user).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = IngredientInputSerializer(many=True)
    image = Base64ImageField(required=True)
    cooking_time = serializers.IntegerField(
        min_value=MIN_COOKING_TIME,
        max_value=MAX_COOKING_TIME,
        error_messages={
            "min_value": f"Минимум {MIN_COOKING_TIME} минут.",
            "max_value": f"Максимум {MAX_COOKING_TIME} минут.",
        },
    )

    class Meta:
        model = Recipe
        fields = (
            "id",
            "ingredients",
            "image",
            "name",
            "text",
            "cooking_time",
            "author",
        )
        read_only_fields = ("id", "author")

    def validate(self, data):
        ingredients = data.get("ingredients")

        if not ingredients:
            raise serializers.ValidationError(
                {"ingredients": "Нужно указать хотя бы один ингредиент."}
            )
        ingredient_ids = [item["id"].id for item in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                {"ingredients": "Ингредиенты не должны повторяться."}
            )

        if not data.get("image") and not self.instance:
            raise serializers.ValidationError(
                {"image": "Поле 'image' обязательно для создания."}
            )

        return data

    def create_ingredients(self, recipe, ingredients_data):
        RecipeIngredientLink.objects.bulk_create(
            [
                RecipeIngredientLink(
                    recipe=recipe,
                    ingredient=item["id"],
                    amount=item["amount"],
                )
                for item in ingredients_data
            ]
        )

    @transaction.atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        image = validated_data.pop("image")

        validated_data["author"] = self.context["request"].user
        recipe = Recipe.objects.create(**validated_data, image=image)
        self.create_ingredients(recipe, ingredients_data)

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients", None)
        image = validated_data.pop("image", None)

        if ingredients_data:
            instance.ingredients.clear()
            self.create_ingredients(instance, ingredients_data)

        if image is not None:
            instance.image = image
            instance.save(update_fields=["image"])
        else:
            raise serializers.ValidationError(
                {"image": "Поле 'image' обязательно для создания."}
            )

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeDetailSerializer(
            instance, context=self.context
        ).data


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = fields


class SubscriptionOutputSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ("recipes",
                                               "recipes_count")

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        limit = self.context["request"].query_params.get("recipes_limit")
        recipes = obj.recipes.all()

        if limit:
            try:
                recipes = recipes[: int(limit)]
            except (ValueError, TypeError):
                pass

        return RecipeShortSerializer(recipes, many=True,
                                     context=self.context).data


class AvatarUpdateSerializer(serializers.Serializer):
    avatar = Base64ImageField(required=True)


class AvatarResponseSerializer(serializers.Serializer):
    avatar = serializers.ImageField(read_only=True)


class SubscriptionSerializer(serializers.Serializer):
    author_id = serializers.IntegerField(write_only=True)

    def validate_author_id(self, value):
        try:
            author = User.objects.get(id=value)
        except User.DoesNotExist:
            raise Http404({
                "author_id": "Пользователь с таким ID не существует."
            })
        return author

    def validate(self, data):
        user = self.context["request"].user
        author = data.get("author_id")
        if not author:
            raise serializers.ValidationError({
                "author_id": "ID пользователя не указан."
            })
        if user == author:
            raise serializers.ValidationError({
                "errors": "Нельзя подписаться на самого себя."
            })
        if UserSubscription.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError({
                "errors": "Вы уже подписаны на этого пользователя."
            })
        return {"author": author}

    def create(self, validated_data):
        user = self.context["request"].user
        author = validated_data["author"]

        return UserSubscription.objects.create(
            user=user,
            author=author
        )
