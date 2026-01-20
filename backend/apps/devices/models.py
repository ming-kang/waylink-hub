from django.db import models


class Device(models.Model):
    """ESP32设备模型"""

    STATUS_CHOICES = [
        ('online', '在线'),
        ('offline', '离线'),
        ('error', '故障'),
    ]

    # 设备基本信息
    device_id = models.CharField(max_length=50, unique=True, verbose_name='设备ID')
    name = models.CharField(max_length=100, blank=True, verbose_name='设备名称')
    station = models.CharField(max_length=50, verbose_name='所属站点')
    location = models.CharField(max_length=100, blank=True, verbose_name='位置描述')

    # 状态信息
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline', verbose_name='在线状态')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')

    # 绑定柜子（一个设备可能控制多个柜子）
    bound_cabinets = models.ManyToManyField('cabinets.Cabinet', related_name='devices', verbose_name='绑定柜子')

    # 安全密钥（ESP32连接时验证）
    api_key = models.CharField(max_length=64, unique=True, verbose_name='API密钥')

    # 心跳相关
    last_heartbeat = models.DateTimeField(null=True, blank=True, verbose_name='最后心跳时间')

    # 电量（如果有电池供电）
    battery_level = models.IntegerField(null=True, blank=True, verbose_name='电量百分比')

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '设备'
        verbose_name_plural = verbose_name
        ordering = ['station', 'device_id']

    def __str__(self):
        return f"{self.device_id} ({self.station}) - {self.get_status_display()}"

    def is_online(self):
        """检查设备是否在线（5分钟内有心跳）"""
        from django.utils import timezone
        if not self.last_heartbeat:
            return False
        from datetime import timedelta
        return timezone.now() - self.last_heartbeat < timedelta(minutes=5)


class DeviceLog(models.Model):
    """设备操作日志"""

    LOG_TYPES = [
        ('open', '开柜'),
        ('close', '关柜'),
        ('heartbeat', '心跳'),
        ('status', '状态上报'),
        ('error', '错误'),
    ]

    device = models.ForeignKey(Device, on_delete=models.CASCADE, verbose_name='设备')
    log_type = models.CharField(max_length=20, choices=LOG_TYPES, verbose_name='日志类型')
    message = models.TextField(blank=True, verbose_name='消息')
    data = models.JSONField(null=True, blank=True, verbose_name='附加数据')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '设备日志'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.device.device_id} - {self.log_type} - {self.created_at}"
