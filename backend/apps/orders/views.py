from decimal import Decimal
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from .models import Order
from django.contrib.auth import get_user_model
from .serializers import OrderSerializer, OrderListSerializer, OrderCreateSerializer, OrderPaymentSerializer, OrderExtendSerializer

User = get_user_model()


class OrderViewSet(viewsets.ModelViewSet):
    """订单视图集"""
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        return OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.filter(user=self.request.user)

        # 筛选状态
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderCreateView(APIView):
    """创建预约订单"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        if serializer.is_valid():
            cabinet = serializer.validated_data['cabinet_id']
            duration = Decimal(str(serializer.validated_data['duration_hours']))

            # 检查柜子是否可用
            if cabinet.status != 'available':
                return Response({
                    'code': 400,
                    'message': '柜子不可用'
                }, status=status.HTTP_400_BAD_REQUEST)

            # 创建订单
            with transaction.atomic():
                # 锁定柜子
                cabinet.status = 'in_use'
                cabinet.save()

                order = Order.objects.create(
                    user=request.user,
                    cabinet=cabinet,
                    duration_hours=duration,
                    price_per_hour=cabinet.price_per_hour,
                    status='pending',
                )

            return Response({
                'code': 0,
                'message': '订单创建成功',
                'data': OrderSerializer(order).data
            }, status=status.HTTP_201_CREATED)

        return Response({
            'code': 400,
            'message': '创建失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class OrderPaymentView(APIView):
    """订单支付"""
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        serializer = OrderPaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'code': 400,
                'message': '支付失败',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.select_for_update().get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({
                'code': 404,
                'message': '订单不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        if order.status != 'pending':
            return Response({
                'code': 400,
                'message': '订单已支付或已取消'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 模拟支付处理
        payment_method = serializer.validated_data['payment_method']

        # 余额支付处理（使用原子操作防止竞态条件）
        if payment_method == 'balance':
            from django.db.models import F
            updated = User.objects.filter(
                id=request.user.id,
                balance__gte=order.total_amount
            ).update(balance=F('balance') - order.total_amount)

            if updated == 0:
                return Response({
                    'code': 400,
                    'message': '余额不足'
                }, status=status.HTTP_400_BAD_REQUEST)

            # 重新加载用户以获取更新后的余额
            request.user.refresh_from_db()

        # 更新订单状态
        now = timezone.now()
        order.status = 'paid'
        order.payment_method = payment_method
        order.paid_at = now
        order.start_time = now
        order.end_time = now + timezone.timedelta(hours=float(order.duration_hours))
        order.save()

        return Response({
            'code': 0,
            'message': '支付成功',
            'data': OrderSerializer(order).data
        })


class OrderDetailView(APIView):
    """订单详情"""
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({
                'code': 404,
                'message': '订单不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'code': 0,
            'message': 'success',
            'data': OrderSerializer(order).data
        })


class MyOrdersView(APIView):
    """我的订单列表"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Order.objects.filter(user=request.user)

        # 筛选状态
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        serializer = OrderListSerializer(queryset, many=True)
        return Response({
            'code': 0,
            'message': 'success',
            'data': serializer.data
        })


class OrderExtendView(APIView):
    """订单续费"""
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        serializer = OrderExtendSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'code': 400,
                'message': '续费失败',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({
                'code': 404,
                'message': '订单不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        if order.status not in ['paid', 'in_use']:
            return Response({
                'code': 400,
                'message': '订单状态不支持续费'
            }, status=status.HTTP_400_BAD_REQUEST)

        additional_hours = Decimal(str(serializer.validated_data['additional_hours']))
        additional_amount = additional_hours * order.price_per_hour

        # 延长结束时间
        order.end_time = order.end_time + timezone.timedelta(hours=float(additional_hours))
        order.total_amount += additional_amount
        order.duration_hours += additional_hours
        order.save()

        return Response({
            'code': 0,
            'message': '续费成功',
            'data': OrderSerializer(order).data
        })


class OrderCancelView(APIView):
    """取消订单"""
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({
                'code': 404,
                'message': '订单不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        if order.status != 'pending':
            return Response({
                'code': 400,
                'message': '只有待支付的订单可以取消'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 释放柜子
        order.cabinet.status = 'available'
        order.cabinet.save()

        # 更新订单状态
        order.status = 'cancelled'
        order.save()

        return Response({
            'code': 0,
            'message': '订单已取消',
            'data': OrderSerializer(order).data
        })
