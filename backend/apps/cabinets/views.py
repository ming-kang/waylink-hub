from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

from .models import Cabinet
from .serializers import CabinetSerializer, CabinetListSerializer, CabinetStatusSerializer, CabinetCreateSerializer


class CabinetListView(APIView):
    """储物柜列表"""
    permission_classes = [AllowAny]

    def get(self, request):
        queryset = Cabinet.objects.all()

        # 筛选站点
        station = request.query_params.get('station')
        if station:
            queryset = queryset.filter(station=station)

        # 筛选尺寸
        size = request.query_params.get('size')
        if size:
            queryset = queryset.filter(size=size)

        # 筛选状态
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        serializer = CabinetListSerializer(queryset, many=True)
        return Response({
            'code': 0,
            'message': 'success',
            'data': serializer.data
        })


class CabinetDetailView(APIView):
    """储物柜详情"""
    permission_classes = [AllowAny]

    def get(self, request, cabinet_id):
        try:
            cabinet = Cabinet.objects.get(cabinet_id=cabinet_id)
        except Cabinet.DoesNotExist:
            return Response({
                'code': 404,
                'message': '柜子不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'code': 0,
            'message': 'success',
            'data': CabinetSerializer(cabinet).data
        })


class CabinetStatusView(APIView):
    """获取柜子实时状态"""
    permission_classes = [AllowAny]

    def get(self, request, cabinet_id):
        try:
            cabinet = Cabinet.objects.get(cabinet_id=cabinet_id)
        except Cabinet.DoesNotExist:
            return Response({
                'code': 404,
                'message': '柜子不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'code': 0,
            'message': 'success',
            'data': CabinetStatusSerializer(cabinet).data
        })


class AvailableCabinetsView(APIView):
    """获取可用柜子列表"""
    permission_classes = [AllowAny]

    def get(self, request):
        station = request.query_params.get('station')
        size = request.query_params.get('size')

        queryset = Cabinet.objects.filter(status='available')

        if station:
            queryset = queryset.filter(station=station)
        if size:
            queryset = queryset.filter(size=size)

        serializer = CabinetListSerializer(queryset, many=True)
        return Response({
            'code': 0,
            'message': 'success',
            'data': serializer.data
        })


class CabinetCreateView(APIView):
    """创建柜子（管理员）"""
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = CabinetCreateSerializer(data=request.data)
        if serializer.is_valid():
            cabinet = serializer.save()
            return Response({
                'code': 0,
                'message': '创建成功',
                'data': CabinetSerializer(cabinet).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'code': 400,
            'message': '创建失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
