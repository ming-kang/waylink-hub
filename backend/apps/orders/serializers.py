from decimal import Decimal
from rest_framework import serializers
from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    """订单详情序列化器"""
    cabinet_id = serializers.CharField(source='cabinet.cabinet_id', read_only=True)
    cabinet_size = serializers.CharField(source='cabinet.size', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'order_no', 'user', 'user_phone', 'cabinet', 'cabinet_id', 'cabinet_size',
            'created_at', 'paid_at', 'start_time', 'end_time', 'actual_end_time',
            'duration_hours', 'price_per_hour', 'total_amount',
            'status', 'status_display', 'payment_method', 'payment_method_display',
            'pickup_code'
        )
        read_only_fields = (
            'id', 'order_no', 'user', 'created_at', 'paid_at', 'start_time',
            'end_time', 'actual_end_time', 'price_per_hour', 'total_amount',
            'status', 'payment_method', 'pickup_code'
        )


class OrderListSerializer(serializers.ModelSerializer):
    """订单列表序列化器（简化版）"""
    cabinet_id = serializers.CharField(source='cabinet.cabinet_id', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'order_no', 'cabinet_id', 'status', 'status_display',
            'duration_hours', 'total_amount', 'created_at', 'end_time'
        )


class OrderCreateSerializer(serializers.Serializer):
    """创建订单序列化器"""
    cabinet_id = serializers.CharField(required=True, max_length=20, label='柜子编号')
    duration_hours = serializers.DecimalField(required=True, max_digits=6, decimal_places=2, min_value=Decimal('0.5'), label='时长(小时)')

    def validate_cabinet_id(self, value):
        from apps.cabinets.models import Cabinet
        try:
            cabinet = Cabinet.objects.get(cabinet_id=value)
        except Cabinet.DoesNotExist:
            raise serializers.ValidationError('柜子不存在')

        if cabinet.status != 'available':
            raise serializers.ValidationError('柜子不可用')
        return cabinet


class OrderPaymentSerializer(serializers.Serializer):
    """订单支付序列化器"""
    payment_method = serializers.ChoiceField(choices=['wechat', 'alipay', 'balance'], label='支付方式')


class OrderExtendSerializer(serializers.Serializer):
    """续费序列化器"""
    additional_hours = serializers.DecimalField(required=True, max_digits=6, decimal_places=2, min_value=Decimal('0.5'), label='增加时长(小时)')
