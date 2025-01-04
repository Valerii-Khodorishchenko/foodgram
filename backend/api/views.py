from django.contrib.auth import authenticate, get_user_model
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from api.serializers import UserSerializer


User = get_user_model()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    Token.objects.filter(user=request.user).delete()
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    try:
        user = User.objects.get(email=request.data.get('email'))
    except User.DoesNotExist:
        return Response(
            {"error": "Invalid email or password"},
            status=status.HTTP_400_BAD_REQUEST
        )
    user = authenticate(
        username=user.username,
        password=request.data.get('password')
    )
    if not user:
        return Response(
            {"error": "Invalid email or password"},
            status=status.HTTP_400_BAD_REQUEST
        )

    token, created = Token.objects.get_or_create(user=user)
    return Response({"auth_token": token.key}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
