from rest_framework import serializers
from .models import Cabinet


class CabinetSerializer(serializers.ModelSerializer):
    """储物柜详情序列化器"""
    size_display = serializers.CharField(source='get_size_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Cabinet
        fields = (
            'id', 'cabinet_id', 'size', 'size_display', 'location', 'station',
            'status', 'status_display', 'price_per_hour', 'device_id',
            'is_locked', 'lock_angle', 'lock_locked', 'has_item', 'item_detected_at',
            'created_at', 'updated_at'
        )
        read_only_fields = ('status', 'is_locked', 'lock_angle', 'lock_locked',
                           'has_item', 'item_detected_at', 'created_at', 'updated_at')


class CabinetListSerializer(serializers.ModelSerializer):
    """储物柜列表序列化器（简化版）"""
    size_display = serializers.CharField(source='get_size_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Cabinet
        fields = (
            'id', 'cabinet_id', 'size', 'size_display', 'location', 'station',
            'status', 'status_display', 'price_per_hour'
        )


class CabinetStatusSerializer(serializers.ModelSerializer):
    """柜子状态序列化器（实时状态）"""
    size_display = serializers.CharField(source='get_size_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Cabinet
        fields = (
            'id', 'cabinet_id', 'size', 'size_display',
            'status', 'status_display', 'price_per_hour', 'is_locked'
        )


class CabinetCreateSerializer(serializers.ModelSerializer):
    """创建柜子序列化器"""
    class Meta:
        model = Cabinet
        fields = (
            'cabinet_id', 'size', 'location', 'station',
            'price_per_hour', 'device_id'
        )
