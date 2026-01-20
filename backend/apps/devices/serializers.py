from rest_framework import serializers
from .models import Device, DeviceLog


class DeviceSerializer(serializers.ModelSerializer):
    """设备详情序列化器"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    bound_cabinet_ids = serializers.SerializerMethodField()

    class Meta:
        model = Device
        fields = (
            'id', 'device_id', 'name', 'station', 'location',
            'status', 'status_display', 'is_active',
            'bound_cabinet_ids', 'last_heartbeat', 'battery_level',
            'created_at', 'updated_at'
        )
        read_only_fields = ('status', 'last_heartbeat', 'battery_level')

    def get_bound_cabinet_ids(self, obj):
        return list(obj.bound_cabinets.values_list('cabinet_id', flat=True))


class DeviceListSerializer(serializers.ModelSerializer):
    """设备列表序列化器（简化版）"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Device
        fields = (
            'id', 'device_id', 'name', 'station', 'location',
            'status', 'status_display', 'is_active',
            'last_heartbeat', 'battery_level'
        )


class DeviceCreateSerializer(serializers.ModelSerializer):
    """创建设备序列化器"""
    cabinet_ids = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        label='绑定柜子ID列表'
    )

    class Meta:
        model = Device
        fields = ('device_id', 'name', 'station', 'location', 'cabinet_ids', 'api_key')

    def create(self, validated_data):
        cabinet_ids = validated_data.pop('cabinet_ids', [])
        from apps.cabinets.models import Cabinet
        device = Device.objects.create(**validated_data)
        if cabinet_ids:
            cabinets = Cabinet.objects.filter(cabinet_id__in=cabinet_ids)
            device.bound_cabinets.set(cabinets)
        return device


class DeviceHeartbeatSerializer(serializers.Serializer):
    """心跳上报序列化器"""
    battery_level = serializers.IntegerField(required=False, min_value=0, max_value=100, label='电量')


class CabinetStatusSerializer(serializers.Serializer):
    """单个柜子状态序列化器"""
    door = serializers.BooleanField(
        label='柜门状态',
        help_text='true=关闭, false=开启'
    )
    lock_angle = serializers.IntegerField(
        min_value=0,
        max_value=360,
        label='锁舌角度',
        help_text='电机锁舌转动角度(0-360度)'
    )
    lock_locked = serializers.BooleanField(
        label='锁是否锁定',
        help_text='true=锁定, false=解锁'
    )
    has_item = serializers.BooleanField(
        label='是否有物品',
        help_text='true=有物品, false=无物品'
    )


class DeviceStatusReportSerializer(serializers.Serializer):
    """状态上报序列化器"""
    cabinet_status = serializers.DictField(
        child=CabinetStatusSerializer(),
        label='柜子状态',
        help_text='{"A001": {"door": true, "lock_angle": 0, "lock_locked": true, "has_item": false}}'
    )
    battery_level = serializers.IntegerField(required=False, min_value=0, max_value=100, label='电量')


class OpenCabinetSerializer(serializers.Serializer):
    """开柜指令序列化器"""
    cabinet_id = serializers.CharField(required=True, label='柜子ID')
    pickup_code = serializers.CharField(required=True, label='取件码')

    def validate_pickup_code(self, value):
        if len(value) != 6 or not value.isdigit():
            raise serializers.ValidationError('取件码必须是6位数字')
        return value


class OpenCabinetResponseSerializer(serializers.Serializer):
    """开柜响应序列化器"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    cabinet_id = serializers.CharField()
    action = serializers.CharField(help_text='open 或 already_open')


class DeviceLogSerializer(serializers.ModelSerializer):
    """设备日志序列化器"""
    device_id = serializers.CharField(source='device.device_id', read_only=True)

    class Meta:
        model = DeviceLog
        fields = ('id', 'device_id', 'log_type', 'message', 'data', 'created_at')
