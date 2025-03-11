from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
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
from backend.settings import TYPE_FILE_SHOPPING_LIST
from recipe.models import Ingredient, Recipe, Tag, User, Cart


class UserViewSet(DjoserUserViewSet):
    pagination_class = LimitOffsetPagination
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
        user = request.user
        subscriptions = User.objects.filter(following__user=user)
        recipes_limit = request.query_params.get('recipes_limit', None)
        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = SubscribeSerializer(
                page, many=True,
                context={'request': request, 'recipes_limit': recipes_limit}
            )
            return self.get_paginated_response(serializer.data)

        serializer = SubscribeSerializer(
            subscriptions, many=True,
            context={'request': request, 'recipes_limit': recipes_limit}
        )

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
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrAdmin,)
    http_method_names = ('get', 'post', 'patch', 'delete')
    serializer_class = RecipeCreatePatchSerializer

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
        serializer = RecipeCartFavoriteSerializer(
            data=request.data,
            context={
                'request': request,
                'recipe': recipe,
                'category': 'favorite'
            })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if request.method == 'POST':
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=('post', 'delete',), url_path='shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        recipe = self.get_object()
        serializer = RecipeCartFavoriteSerializer(
            data=request.data,
            context={
                'request': request,
                'recipe': recipe,
                'category': 'cart'
            })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if request.method == 'POST':
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=('get',), url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        type_file = TYPE_FILE_SHOPPING_LIST
        user = request.user
        shopping_cart = Recipe.objects.filter(in_carts__user=user).prefetch_related('ingredients').all()
        if type_file == 'csv':
            content = shopping_list.generate_csv_shopping_list(shopping_cart)
            response = HttpResponse(
                content, content_type='text/csv; charset=utf-8')
        elif type_file == 'pdf':
            content = shopping_list.generate_pdf_shopping_list(shopping_cart)
            response = HttpResponse(content, content_type='application/pdf')
        else:
            type_file = 'txt'
            content = shopping_list.generate_txt_shopping_list(shopping_cart)
            response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            f'attachment; filename="shopping_list.{type_file}"'
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
