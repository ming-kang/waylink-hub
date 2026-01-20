from django.db import models
from django.conf import settings
from django.utils import timezone


class Order(models.Model):
    """订单模型"""

    STATUS_CHOICES = [
        ('pending', '待支付'),
        ('paid', '已预约'),
        ('in_use', '使用中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
        ('overdue', '逾期未取'),
    ]

    PAYMENT_CHOICES = [
        ('wechat', '微信支付'),
        ('alipay', '支付宝'),
        ('balance', '余额支付'),
        ('free', '免费'),
    ]

    # 订单基本信息
    order_no = models.CharField(max_length=32, unique=True, verbose_name='订单号')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='用户')

    # 柜子信息
    cabinet = models.ForeignKey('cabinets.Cabinet', on_delete=models.CASCADE, verbose_name='储物柜')

    # 时间信息
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='支付时间')
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='开始使用时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='预计结束时间')
    actual_end_time = models.DateTimeField(null=True, blank=True, verbose_name='实际结束时间')

    # 费用信息
    duration_hours = models.DecimalField(max_digits=6, decimal_places=2, default=1, verbose_name='时长(小时)')
    price_per_hour = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='单价')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='总金额')

    # 状态
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='订单状态')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, blank=True, null=True, verbose_name='支付方式')

    # 开柜码（用户取件用）
    pickup_code = models.CharField(max_length=6, blank=True, null=True, verbose_name='取件码')

    class Meta:
        verbose_name = '订单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order_no} - {self.user.phone} - {self.get_status_display()}"

    def generate_order_no(self):
        """生成订单号"""
        import random
        import string
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"O{timestamp}{random_str}"

    def generate_pickup_code(self):
        """生成取件码"""
        import random
        return ''.join(random.choices('0123456789', k=6))

    def calculate_amount(self):
        """计算总金额"""
        return float(self.price_per_hour) * float(self.duration_hours)

    def save(self, *args, **kwargs):
        if not self.order_no:
            self.order_no = self.generate_order_no()
        if not self.pickup_code and self.status in ['paid', 'in_use']:
            self.pickup_code = self.generate_pickup_code()
        if not self.total_amount:
            self.total_amount = self.calculate_amount()
        super().save(*args, **kwargs)
