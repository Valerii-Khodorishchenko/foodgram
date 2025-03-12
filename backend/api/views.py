from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import viewsets, status
from rest_framework.decorators import action
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
    RecipeCartFavoriteSerializer,
    RecipeCreatePatchSerializer,
    SubscribeSerializer,
    TagSerializer
)
from recipe.models import Cart, Favorites, Ingredient, Recipe, Tag, User


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
        subscriptions = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(subscriptions)
        if page is not None:
            return self.get_paginated_response(
                SubscribeSerializer(
                    page, many=True, context={'request': request}
                ).data
            )
        return Response(SubscribeSerializer(
            subscriptions, many=True, context={'request': request}).data)

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='subscribe',
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        target_user = get_object_or_404(User, id=id)
        recipes_limit = request.query_params.get('recipes_limit', None)
        serializer = SubscribeSerializer(
            target_user,
            data=request.data,
            context={
                'request': request,
                'target_user': target_user,
                'recipes_limit': recipes_limit
            })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if request.method == 'POST':
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrAdmin,)
    http_method_names = ('get', 'post', 'patch', 'delete')
    serializer_class = RecipeCreatePatchSerializer

    @staticmethod
    def handle_favorite_or_cart(request, model, recipe):
        serializer = RecipeCartFavoriteSerializer(recipe)
        category = 'Избранном' if model == Favorites else 'Корзине'
        if request.method == 'POST':
            if not model.objects.filter(
                user=request.user, recipe=recipe
            ).exists():
                model.objects.get_or_create(user=request.user, recipe=recipe)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'error': 'Рецепт уже в {}'.format(category)},
                status=status.HTTP_400_BAD_REQUEST
            )
        if model.objects.filter(user=request.user, recipe=recipe).exists():
            model.objects.filter(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Рецепт отсутствует в {}'.format(category)},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk):
        get_object_or_404(Recipe, pk=pk)
        short_url = request.build_absolute_uri(
            reverse('recipe-short-url', args=[pk])
        )
        return Response({'short-link': short_url}, status=status.HTTP_200_OK)

    @action(
        detail=True, methods=('post', 'delete'), url_path='favorite',
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        recipe = self.get_object()
        return self.handle_favorite_or_cart(request, Favorites, recipe)

    @action(
        detail=True, methods=('post', 'delete',), url_path='shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        recipe = self.get_object()
        return self.handle_favorite_or_cart(request, Cart, recipe)

    @action(
        detail=False, methods=('get',), url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart = Recipe.objects.filter(
            in_carts__user=user).prefetch_related('ingredients').all()
        content = shopping_list.generate_txt_shopping_list(shopping_cart)
        response = FileResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            f'attachment; filename="shopping_list.txt"'
        )
        return response


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
