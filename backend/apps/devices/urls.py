from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DeviceViewSet, DeviceLogsView,
    DeviceHeartbeatView, DeviceStatusReportView, DeviceOpenCabinetView, OpenCabinetByCodeView,
    DeviceStatusQueryView, CabinetStatusQueryView
)

router = DefaultRouter()
router.register('', DeviceViewSet, basename='device')

urlpatterns = [
    # ESP32 设备通信接口
    path('heartbeat/', DeviceHeartbeatView.as_view(), name='device-heartbeat'),
    path('status/', DeviceStatusReportView.as_view(), name='device-status'),
    path('status/query/<str:device_id>/', DeviceStatusQueryView.as_view(), name='device-status-query'),
    path('open/by-code/', OpenCabinetByCodeView.as_view(), name='open-by-code'),
    path('<str:device_id>/open/', DeviceOpenCabinetView.as_view(), name='device-open'),
    path('<str:device_id>/logs/', DeviceLogsView.as_view(), name='device-logs'),

    # 管理员查询接口
    path('query/<str:device_id>/', CabinetStatusQueryView.as_view(), name='cabinet-status-query'),

    # 设备管理接口
    path('manage/', include(router.urls)),
]
