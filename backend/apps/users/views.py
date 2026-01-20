from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer, UserRegisterSerializer, LoginSerializer

User = get_user_model()


class RegisterView(APIView):
    """用户注册"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'code': 0,
                'message': '注册成功',
                'data': {
                    'user': UserSerializer(user).data,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            }, status=status.HTTP_201_CREATED)
        return Response({
            'code': 400,
            'message': '注册失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """用户登录"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            password = serializer.validated_data['password']

            try:
                user = User.objects.get(phone=phone)
            except User.DoesNotExist:
                return Response({
                    'code': 400,
                    'message': '手机号或密码错误'
                }, status=status.HTTP_400_BAD_REQUEST)

            if not user.check_password(password):
                return Response({
                    'code': 400,
                    'message': '手机号或密码错误'
                }, status=status.HTTP_400_BAD_REQUEST)

            refresh = RefreshToken.for_user(user)
            return Response({
                'code': 0,
                'message': '登录成功',
                'data': {
                    'user': UserSerializer(user).data,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            })
        return Response({
            'code': 400,
            'message': '登录失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """当前用户信息"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'code': 0,
            'message': 'success',
            'data': UserSerializer(request.user).data
        })


class UserDetailView(APIView):
    """指定用户信息"""
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'code': 404,
                'message': '用户不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'code': 0,
            'message': 'success',
            'data': UserSerializer(user).data
        })
