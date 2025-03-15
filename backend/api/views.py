from django.db.models import Sum
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from api import shopping_list
from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthorOrAdmin
from api.serializers import (
    AvatarSerializer,
    IngredientSerializer,
    ReadRecipeSerializer,
    RecipeCreatePatchSerializer,
    RecipeSerializer,
    SubscriptionReaderSerializer,
    TagSerializer
)
from recipe.models import (
    Cart,
    Favorites,
    Follow,
    Ingredient,
    Recipe,
    RecipeComponent,
    Tag,
    User
)


class UserViewSet(DjoserUserViewSet):
    http_method_names = ('get', 'post', 'put', 'delete')

    @action(
        detail=False, methods=['get'], url_path='me',
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(
        detail=False, methods=['put', 'delete'], url_path='me/avatar',
        permission_classes=(IsAuthenticated,),
    )
    def avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializers = AvatarSerializer(user, data=request.data)
            serializers.is_valid(raise_exception=True)
            serializers.save()
            return Response(serializers.data, status=status.HTTP_200_OK)
        user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=('get',), url_path='subscriptions',
        permission_classes=(IsAuthenticated,)
    )
    def get_subscriptions(self, request):
        subscriptions = User.objects.filter(authors__user=request.user)
        page = self.paginate_queryset(subscriptions)
        return self.get_paginated_response(
            SubscriptionReaderSerializer(
                page, many=True, context={'request': request}
            ).data
        )

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='subscribe',
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        user = request.user
        if request.method == 'POST':
            if author == user:
                raise ValidationError({'error': 'Нельзя подписаться на себя.'})
            follow, created = Follow.objects.get_or_create(
                user=user, following=author
            )
            if not created:
                raise ValidationError(
                    {'error': 'Вы уже подписаны на этого пользователя.'})
            serializer = SubscriptionReaderSerializer(
                author,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        try:
            follow = get_object_or_404(Follow, user=user, following=author)
        except Http404:
            raise ValidationError(
                {'error': 'Вы не подписаны на этого пользователя.'}
            )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrAdmin,)
    http_method_names = ('get', 'post', 'patch', 'delete')
    serializer_class = RecipeCreatePatchSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=False
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(RecipeSerializer(
            instance, context={'request': request, 'recipe_id': instance.id}
        ).data)

    @staticmethod
    def handle_favorite_or_cart(request, model, pk):
        category = model._meta.verbose_name
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            obj, created = model.objects.get_or_create(
                user=request.user, recipe=recipe
            )
            if created:
                serializer = ReadRecipeSerializer(recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)
            raise ValidationError(
                {'error': f'В категории <{category}> рецепт уже добавлен.'})
        if model.objects.filter(user=request.user, recipe=recipe).exists():
            obj = model.objects.get(user=request.user, recipe=recipe)
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise ValidationError(
            {'error': f'Рецепт отсутствует в категории <{category}>'})

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk):
        if not Recipe.objects.filter(pk=pk).exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response({'short-link': request.build_absolute_uri(
            reverse('recipe:recipe-short-url', args=[pk])
        )}, status=status.HTTP_200_OK)

    @action(
        detail=True, methods=('post', 'delete'), url_path='favorite',
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        return self.handle_favorite_or_cart(request, Favorites, pk)

    @action(
        detail=True, methods=('post', 'delete',), url_path='shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return self.handle_favorite_or_cart(request, Cart, pk)

    @action(
        detail=False, methods=('get',), url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart_resipes = Recipe.objects.filter(
            carts__user=user).all()
        shopping_cart_ingredients = RecipeComponent.objects.filter(
            recipe__carts__user=user
        ).values(
            'product__name', 'product__measurement_unit'
        ).annotate(
            amount=Sum('amount')
        )
        content = shopping_list.generate_txt_shopping_list(
            shopping_cart_ingredients, shopping_cart_resipes
        )
        return FileResponse(
            content,
            content_type='text/plain',
            headers={
                'Content-Disposition':
                'attachment; filename="shopping_list.txt"'
            }
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


def redoc_view(request):
    return render(request, 'redoc.html')
