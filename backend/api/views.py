from django.shortcuts import redirect
from django.http import Http404
from django.urls import reverse
from hashids import Hashids
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    AllowAny,
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
    LoginSerializer,
    PasswordSerializer,
    RecipeCartFavoriteSerializer,
    RecipeCreatePatchSerializer,
    SignupSerializer,
    SubscribeSerializer,
    TagSerializer,
    UserSerializer
)
from recipe.models import Ingredient, Recipe, Tag, User
from recipe.constants import TYPE_FILE_SHOPPING_LIST


class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token, created = Token.objects.get_or_create(
            user=serializer.validated_data
        )
        return Response({"auth_token": token.key}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    request.auth.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination
    http_method_names = ('get', 'post', 'put', 'delete')

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return SignupSerializer
        return super().get_serializer_class()

    @action(
        detail=False,
        methods=('get',),
        url_path='me',
        permission_classes=(IsAuthenticated,)
    )
    def user_profile(self, request):
        return Response(self.get_serializer(request.user).data)

    @action(
        detail=False,
        methods=('put', 'delete'),
        url_path='me/avatar',
        permission_classes=(IsAuthenticated,),
    )
    def user_avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializers = AvatarSerializer(user, data=request.data)
            serializers.is_valid(raise_exception=True)
            serializers.save()
            return Response(serializers.data, status=status.HTTP_200_OK)
        user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('post',),
        url_path='set_password',
        permission_classes=(IsAuthenticated,),
    )
    def set_password(self, request):
        user = request.user
        serializer = PasswordSerializer(
            data=request.data, context={'user': user}
        )
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        url_path='subscriptions',
        permission_classes=(IsAuthenticated,),
    )
    def get_subscriptions(self, request):
        user = request.user
        subscriptions = user.followings.all()
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
        return Response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='subscribe',
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, pk):
        target_user = get_object_or_404(User, id=pk)
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


def redirect_short_link(request, short_id):
    hashids = Hashids(min_length=6)
    try:
        recipe_id = hashids.decode(short_id)[0]
        recipe = Recipe.objects.get(id=recipe_id)
        return redirect('recipe-detail', pk=recipe.id)
    except (IndexError, Recipe.DoesNotExist):
        raise Http404("Рецепт не найден")


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
        try:
            recipe = self.get_object()
            hashids = Hashids(min_length=6)
            short_id = hashids.encode(recipe.id)
            short_url = request.build_absolute_uri(
                reverse('recipe-short-url', kwargs={'short_id': short_id}))
            return Response(
                {'short-link': short_url},
                status=status.HTTP_200_OK
            )
        except Recipe.DoesNotExist:
            return Response(
                {'detail': 'Рецепт не найден.'},
                status=status.HTTP_404_NOT_FOUND
            )

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
        shopping_cart = user.cart.prefetch_related('ingredients').all()
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
