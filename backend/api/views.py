from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import (
    filters as drf_filters,
    serializers,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredientLink,
    ShoppingListEntry,
)
from users.models import User

from .filters import IngredientSearchFilter, RecipeCustomFilter
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    AvatarResponseSerializer,
    AvatarUpdateSerializer,
    IngredientSerializer,
    RecipeDetailSerializer,
    RecipeShortSerializer,
    RecipeWriteSerializer,
    SubscriptionOutputSerializer,
    SubscriptionSerializer,
    UserSerializer,
)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all().order_by('name')
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientSearchFilter


class CustomPaginator(PageNumberPagination):
    page_size_query_param = "limit"


class CustomUserManagerViewSet(DjoserUserViewSet):
    pagination_class = CustomPaginator
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == "retrieve":
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        authors = User.objects.filter(following__user=request.user)
        paginated = self.paginate_queryset(authors)
        serializer = SubscriptionOutputSerializer(
            paginated, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id=None):
        serializer = SubscriptionSerializer(
            data={"author_id": id},
            context={"request": request}
        )

        if request.method == "POST":
            try:
                serializer.is_valid(raise_exception=True)
                serializer.save()
                output_serializer = SubscriptionOutputSerializer(
                    serializer.validated_data["author"],
                    context={"request": request}
                )
                return Response(output_serializer.data,
                                status=status.HTTP_201_CREATED)
            except serializers.ValidationError as e:
                return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == "DELETE":
            author = get_object_or_404(User, id=id)
            exists = request.user.follower.filter(author=author).exists()

            if not exists:
                return Response(
                    {"errors": "Вы не были подписаны на этого пользователя."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            request.user.follower.filter(author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["put", "delete"],
        permission_classes=[IsAuthenticated],
        url_path="me/avatar",
        serializer_class=AvatarUpdateSerializer,
    )
    def change_avatar(self, request):
        user = request.user
        if request.method == "PUT":
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            avatar = serializer.validated_data.get("avatar")
            if user.avatar:
                user.avatar.delete(save=False)
            user.avatar = avatar
            user.save(update_fields=["avatar"])
            response_serializer = AvatarResponseSerializer(
                user, context={"request": request}
            )
            return Response(response_serializer.data,
                            status=status.HTTP_200_OK)

        elif request.method == "DELETE":
            if not user.avatar:
                return Response(
                    {"errors": "У пользователя нет аватара для удаления."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.avatar.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class RecipeManagerViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, drf_filters.OrderingFilter]
    filterset_class = RecipeCustomFilter
    ordering_fields = ["name", "pub_date", "cooking_time"]
    ordering = ["-pub_date"]
    pagination_class = CustomPaginator

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RecipeDetailSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def _handle_user_recipe_relation(
        self,
        request,
        pk,
        model_class,
        error_exists,
        error_missing,
    ):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        relation_exists = model_class.objects.filter(
            user=user, recipe=recipe
        ).exists()

        if request.method == "POST":
            if relation_exists:
                return Response(
                    {"errors": error_exists},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            model_class.objects.create(user=user, recipe=recipe)
            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == "DELETE":
            if not relation_exists:
                return Response(
                    {"errors": error_missing},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            model_class.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        return self._handle_user_recipe_relation(
            request,
            pk,
            FavoriteRecipe,
            "Рецепт уже в закладках.",
            "Рецепта не было в закладках.",
        )

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        return self._handle_user_recipe_relation(
            request,
            pk,
            ShoppingListEntry,
            "Рецепт уже в списке покупок.",
            "Рецепта не было в списке покупок.",
        )

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        user = request.user
        ids = ShoppingListEntry.objects.filter(user=user).values_list(
            "recipe__id", flat=True
        )
        if not ids:
            return Response(
                {"errors": "Ваш список покупок пуст."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ingredients = (
            RecipeIngredientLink.objects.filter(recipe__id__in=ids)
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(total_amount=Sum("amount"))
            .order_by("ingredient__name")
        )

        content = "Список покупок:"
        for item in ingredients:
            name = item["ingredient__name"]
            unit = item["ingredient__measurement_unit"]
            amount = item["total_amount"]
            content += f"- {name} ({unit}) — {amount}"

        response = HttpResponse(content, content_type="text/plain")
        response["Content-Disposition"] = 'attachment; filename="cart.txt"'
        return response

    @action(
        detail=True,
        methods=["get"],
        permission_classes=[AllowAny],
        url_path="get-link",
    )
    def generate_short_url(self, request, pk=None):
        recipe = self.get_object()
        try:
            full_url = request.build_absolute_uri(
                reverse("recipes-detail", kwargs={"pk": recipe.pk})
            )
        except Exception:
            return Response(
                {"detail": "Ошибка генерации ссылки."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response({"short-link": full_url}, status=status.HTTP_200_OK)

    def get_queryset(self):
        queryset = super().get_queryset()

        user_id = self.kwargs.get("user_id")
        if user_id:
            return queryset.filter(author_id=user_id)

        if "favorites" in self.request.query_params:
            return Recipe.objects.filter(favorited_by__user=self.request.user)

        if "shopping_cart" in self.request.query_params:
            return Recipe.objects.filter(
                in_shopping_cart_of__user=self.request.user
            )

        return queryset
