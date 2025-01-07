import base64

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.files.base import ContentFile
from rest_framework import serializers

from recipe.constants import MAX_PASSWORD_LENGTH

from recipe.validators import (
    validate_current_password,
    validate_new_password,
    validate_user_credentials
)

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(
                base64.b64decode(imgstr), name='temp.' + ext
            )
        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        )

    def get_is_subscribed(self, obj):
        if (
            (request := self.context.get('request'))
            and request.user.is_authenticated
        ):
            return obj.followings.filter(id=request.user.id).exists()
        return False


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=MAX_PASSWORD_LENGTH, write_only=True,
        validators=[validate_password]
    )

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        data = validate_user_credentials(
            data.get('email'), data.get('password')
        )
        return data


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(
        required=True,
        error_messages={
            "invalid": "Файл не является корректным изображением.",
            "required": "Обязательное поле.",
            "empty": "Вы отправили пустой файл.",
        },
    )

    class Meta:
        model = User
        fields = ('avatar',)


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        required=True, validators=[validate_password]
    )
    current_password = serializers.CharField(required=True)

    def validate(self, passwords):
        validate_new_password(
            passwords['current_password'],
            passwords['new_password']
        )
        return passwords

    def validate_current_password(self, current_password):
        return validate_current_password(
            self.context.get('user'), current_password)
