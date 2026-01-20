from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """用户详情序列化器"""
    class Meta:
        model = User
        fields = ('id', 'username', 'phone', 'email', 'avatar', 'balance', 'created_at')
        read_only_fields = ('id', 'balance', 'created_at')


class UserRegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'phone', 'password', 'password2', 'email')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': '两次密码不一致'})
        if User.objects.filter(phone=attrs['phone']).exists():
            raise serializers.ValidationError({'phone': '该手机号已注册'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """登录序列化器"""
    phone = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class TokenResponseSerializer(serializers.Serializer):
    """Token响应序列化器"""
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()
