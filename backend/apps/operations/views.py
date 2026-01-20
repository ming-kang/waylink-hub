from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Avg, Sum
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from apps.orders.models import Order
from apps.cabinets.models import Cabinet
from apps.devices.models import Device, DeviceLog

User = get_user_model()


class DashboardStatsView(APIView):
    """运维仪表盘统计数据"""
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 时间范围（默认最近7天）
        days = int(request.query_params.get('days', 7))
        start_date = timezone.now() - timedelta(days=days)

        # 基本统计
        total_users = User.objects.count()
        total_orders = Order.objects.count()
        total_cabinets = Cabinet.objects.count()
        total_devices = Device.objects.count()

        # 订单统计
        orders = Order.objects.filter(created_at__gte=start_date)
        order_stats = {
            'total': orders.count(),
            'completed': orders.filter(status='completed').count(),
            'cancelled': orders.filter(status='cancelled').count(),
            'total_amount': float(orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0),
        }

        # 柜子使用率
        cabinet_stats = {
            'total': total_cabinets,
            'available': Cabinet.objects.filter(status='available').count(),
            'in_use': Cabinet.objects.filter(status='in_use').count(),
            'maintenance': Cabinet.objects.filter(status='maintenance').count(),
        }

        # 设备状态
        device_stats = {
            'total': total_devices,
            'online': Device.objects.filter(status='online').count(),
            'offline': Device.objects.filter(status='offline').count(),
            'error': Device.objects.filter(status='error').count(),
        }

        # 每日订单趋势
        daily_orders = []
        for i in range(days):
            day_start = timezone.now() - timedelta(days=days - i - 1)
            day_end = day_start + timedelta(days=1)
            day_count = Order.objects.filter(
                created_at__gte=day_start,
                created_at__lt=day_end
            ).count()
            daily_orders.append({
                'date': day_start.strftime('%Y-%m-%d'),
                'count': day_count
            })

        # 高峰时段分析
        hourly_orders = Order.objects.filter(
            created_at__gte=start_date
        ).extra(
            {'hour': "strftime('%%H', created_at)"}
        ).values('hour').annotate(count=Count('id'))

        peak_hours = sorted(
            [{'hour': int(h['hour']), 'count': h['count']} for h in hourly_orders],
            key=lambda x: x['count'],
            reverse=True
        )[:5]

        return Response({
            'code': 0,
            'message': 'success',
            'data': {
                'overview': {
                    'total_users': total_users,
                    'total_orders': total_orders,
                    'total_cabinets': total_cabinets,
                    'total_devices': total_devices,
                },
                'orders': order_stats,
                'cabinets': cabinet_stats,
                'devices': device_stats,
                'daily_orders': daily_orders,
                'peak_hours': peak_hours,
            }
        })


class AllOrdersView(APIView):
    """所有订单列表（管理员）"""
    permission_classes = [IsAdminUser]

    def get(self, request):
        queryset = Order.objects.all()

        # 筛选状态
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # 筛选站点
        station = request.query_params.get('station')
        if station:
            queryset = queryset.filter(cabinet__station=station)

        # 时间筛选
        date_from = request.query_params.get('from')
        date_to = request.query_params.get('to')
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        # 分页
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size

        total = queryset.count()
        orders = queryset[start:end]

        from apps.orders.serializers import OrderSerializer
        return Response({
            'code': 0,
            'message': 'success',
            'data': {
                'total': total,
                'page': page,
                'page_size': page_size,
                'orders': OrderSerializer(orders, many=True).data
            }
        })


class AdminCabinetsView(APIView):
    """柜子管理（管理员）"""
    permission_classes = [IsAdminUser]

    def get(self, request):
        """获取所有柜子"""
        queryset = Cabinet.objects.all()

        station = request.query_params.get('station')
        if station:
            queryset = queryset.filter(station=station)

        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        from apps.cabinets.serializers import CabinetSerializer
        return Response({
            'code': 0,
            'message': 'success',
            'data': CabinetSerializer(queryset, many=True).data
        })

    def put(self, request):
        """更新柜子"""
        cabinet_id = request.data.get('cabinet_id')
        if not cabinet_id:
            return Response({
                'code': 400,
                'message': '缺少柜子编号'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            cabinet = Cabinet.objects.get(cabinet_id=cabinet_id)
        except Cabinet.DoesNotExist:
            return Response({
                'code': 404,
                'message': '柜子不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        # 可更新字段
        updatable_fields = ['status', 'price_per_hour', 'location']
        for field in updatable_fields:
            if field in request.data:
                setattr(cabinet, field, request.data[field])
        cabinet.save()

        from apps.cabinets.serializers import CabinetSerializer
        return Response({
            'code': 0,
            'message': '更新成功',
            'data': CabinetSerializer(cabinet).data
        })


class AdminDevicesView(APIView):
    """设备管理（管理员）"""
    permission_classes = [IsAdminUser]

    def get(self, request):
        """获取所有设备"""
        queryset = Device.objects.all()

        station = request.query_params.get('station')
        if station:
            queryset = queryset.filter(station=station)

        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        from apps.devices.serializers import DeviceSerializer
        return Response({
            'code': 0,
            'message': 'success',
            'data': DeviceSerializer(queryset, many=True).data
        })

    def put(self, request):
        """更新设备"""
        device_id = request.data.get('device_id')
        if not device_id:
            return Response({
                'code': 400,
                'message': '缺少设备ID'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            device = Device.objects.get(device_id=device_id)
        except Device.DoesNotExist:
            return Response({
                'code': 404,
                'message': '设备不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        # 可更新字段
        updatable_fields = ['name', 'station', 'location', 'is_active']
        for field in updatable_fields:
            if field in request.data:
                setattr(device, field, request.data[field])
        device.save()

        from apps.devices.serializers import DeviceSerializer
        return Response({
            'code': 0,
            'message': '更新成功',
            'data': DeviceSerializer(device).data
        })


class FaultAlertsView(APIView):
    """故障预警列表"""
    permission_classes = [IsAdminUser]

    def get(self, request):
        """获取所有异常告警"""
        alerts = []

        # 离线设备（超过10分钟无心跳）
        offline_threshold = timezone.now() - timedelta(minutes=10)
        offline_devices = Device.objects.filter(
            is_active=True,
            last_heartbeat__lt=offline_threshold
        )
        for device in offline_devices:
            alerts.append({
                'type': 'device_offline',
                'level': 'warning',
                'title': '设备离线',
                'message': f'设备 {device.device_id} ({device.station}) 已离线',
                'device_id': device.device_id,
                'station': device.station,
                'created_at': timezone.now().isoformat(),
            })

        # 低电量设备（低于20%）
        low_battery = Device.objects.filter(
            is_active=True,
            battery_level__lt=20,
            battery_level__isnull=False
        )
        for device in low_battery:
            alerts.append({
                'type': 'low_battery',
                'level': 'warning',
                'title': '设备电量低',
                'message': f'设备 {device.device_id} 电量仅剩 {device.battery_level}%',
                'device_id': device.device_id,
                'station': device.station,
                'battery_level': device.battery_level,
                'created_at': timezone.now().isoformat(),
            })

        # 逾期订单（超过结束时间未取件）
        overdue_orders = Order.objects.filter(
            status='in_use',
            end_time__lt=timezone.now()
        )
        for order in overdue_orders:
            cabinet = order.cabinet
            alerts.append({
                'type': 'order_overdue',
                'level': 'warning',
                'title': '订单逾期',
                'message': f'订单 {order.order_no} 柜子 {cabinet.cabinet_id} 已逾期',
                'order_id': order.id,
                'cabinet_id': cabinet.cabinet_id,
                'station': cabinet.station,
                'created_at': timezone.now().isoformat(),
            })

        # 维护中柜子
        maintenance_cabinets = Cabinet.objects.filter(status='maintenance')
        for cabinet in maintenance_cabinets:
            alerts.append({
                'type': 'cabinet_maintenance',
                'level': 'info',
                'title': '柜子维护中',
                'message': f'柜子 {cabinet.cabinet_id} 正在维护',
                'cabinet_id': cabinet.cabinet_id,
                'station': cabinet.station,
                'created_at': timezone.now().isoformat(),
            })

        return Response({
            'code': 0,
            'message': 'success',
            'data': {
                'total': len(alerts),
                'alerts': alerts
            }
        })


class RevenueStatsView(APIView):
    """收入统计"""
    permission_classes = [IsAdminUser]

    def get(self, request):
        """获取收入统计"""
        # 时间范围
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)

        # 收入统计
        orders = Order.objects.filter(
            created_at__gte=start_date,
            status__in=['paid', 'in_use', 'completed']
        )

        # 按天统计
        daily_revenue = []
        for i in range(days):
            day_start = timezone.now() - timedelta(days=days - i - 1)
            day_end = day_start + timedelta(days=1)
            day_orders = orders.filter(created_at__gte=day_start, created_at__lt=day_end)
            daily_revenue.append({
                'date': day_start.strftime('%Y-%m-%d'),
                'revenue': float(day_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0),
                'orders': day_orders.count()
            })

        # 按站点统计
        station_revenue = []
        stations = orders.values('cabinet__station').annotate(
            revenue=Sum('total_amount'),
            orders=Count('id')
        )
        for s in stations:
            station_revenue.append({
                'station': s['cabinet__station'],
                'revenue': float(s['revenue'] or 0),
                'orders': s['orders']
            })

        return Response({
            'code': 0,
            'message': 'success',
            'data': {
                'total_revenue': float(orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0),
                'total_orders': orders.count(),
                'average_order': float(orders.aggregate(Avg('total_amount'))['total_amount__avg'] or 0),
                'daily_revenue': daily_revenue,
                'station_revenue': station_revenue,
            }
        })
