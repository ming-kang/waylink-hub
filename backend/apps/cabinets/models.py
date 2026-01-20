from django.db import models


class Cabinet(models.Model):
    """储物柜模型"""

    SIZE_CHOICES = [
        ('small', '小柜（放背包）'),
        ('medium', '中柜（放行李箱）'),
        ('large', '大柜（放多个行李）'),
    ]

    STATUS_CHOICES = [
        ('available', '空闲'),
        ('in_use', '使用中'),
        ('maintenance', '维护中'),
        ('offline', '离线'),
    ]

    # 基本信息
    cabinet_id = models.CharField(max_length=20, unique=True, verbose_name='柜子编号')
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, verbose_name='尺寸规格')
    location = models.CharField(max_length=100, verbose_name='位置描述')
    station = models.CharField(max_length=50, verbose_name='所属站点')

    # 状态信息
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name='状态')

    # 费率 (元/小时)
    price_per_hour = models.DecimalField(max_digits=6, decimal_places=2, default=2.00, verbose_name='单价')

    # ESP32 设备绑定
    device_id = models.CharField(max_length=50, blank=True, null=True, verbose_name='绑定设备ID')

    # 柜门状态
    is_locked = models.BooleanField(default=True, verbose_name='是否锁定')

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '储物柜'
        verbose_name_plural = verbose_name
        ordering = ['station', 'cabinet_id']

    def __str__(self):
        return f"{self.cabinet_id} ({self.get_size_display()}) - {self.get_status_display()}"
