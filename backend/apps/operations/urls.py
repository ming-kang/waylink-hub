from django.urls import path
from .views import (
    DashboardStatsView,
    AllOrdersView,
    AdminCabinetsView,
    AdminDevicesView,
    FaultAlertsView,
    RevenueStatsView
)

urlpatterns = [
    # 仪表盘统计
    path('stats/', DashboardStatsView.as_view(), name='admin-stats'),

    # 收入统计
    path('revenue/', RevenueStatsView.as_view(), name='admin-revenue'),

    # 订单管理
    path('orders/', AllOrdersView.as_view(), name='admin-orders'),

    # 柜子管理
    path('cabinets/', AdminCabinetsView.as_view(), name='admin-cabinets'),

    # 设备管理
    path('devices/', AdminDevicesView.as_view(), name='admin-devices'),

    # 故障预警
    path('alerts/', FaultAlertsView.as_view(), name='admin-alerts'),
]
