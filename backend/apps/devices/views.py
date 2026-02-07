import uuid
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

from .models import Device, DeviceLog
from .serializers import (
    DeviceSerializer, DeviceListSerializer, DeviceCreateSerializer,
    DeviceHeartbeatSerializer, DeviceStatusReportSerializer,
    OpenCabinetSerializer, DeviceLogSerializer
)


# ============================================
# ESP32 设备通信接口（无需认证）
# ============================================

@method_decorator(csrf_exempt, name='dispatch')
class DeviceHeartbeatView(APIView):
    """设备心跳上报"""
    permission_classes = [AllowAny]

    def post(self, request):
        """ESP32 定期调用此接口上报心跳"""
        api_key = request.headers.get('X-API-Key') or request.data.get('api_key')

        if not api_key:
            return Response({
                'code': 400,
                'message': '缺少API密钥'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            device = Device.objects.get(api_key=api_key, is_active=True)
        except Device.DoesNotExist:
            return Response({
                'code': 401,
                'message': '无效的API密钥'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # 更新心跳时间
        battery_level = request.data.get('battery_level')
        device.last_heartbeat = timezone.now()
        device.status = 'online'
        if battery_level is not None:
            device.battery_level = battery_level
        device.save()

        # 记录日志
        DeviceLog.objects.create(
            device=device,
            log_type='heartbeat',
            message='心跳上报',
            data={'battery_level': battery_level}
        )

        return Response({
            'code': 0,
            'message': '心跳接收成功',
            'data': {
                'device_id': device.device_id,
                'status': device.status
            }
        })


@method_decorator(csrf_exempt, name='dispatch')
class DeviceStatusReportView(APIView):
    """设备状态上报"""
    permission_classes = [AllowAny]

    def post(self, request):
        """ESP32 上报柜子状态变化"""
        api_key = request.headers.get('X-API-Key') or request.data.get('api_key')

        if not api_key:
            return Response({
                'code': 400,
                'message': '缺少API密钥'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            device = Device.objects.get(api_key=api_key, is_active=True)
        except Device.DoesNotExist:
            return Response({
                'code': 401,
                'message': '无效的API密钥'
            }, status=status.HTTP_401_UNAUTHORIZED)

        serializer = DeviceStatusReportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'code': 400,
                'message': '数据格式错误',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # 更新柜子状态
        cabinet_status = serializer.validated_data['cabinet_status']
        for cabinet_id, status_data in cabinet_status.items():
            try:
                cabinet = device.bound_cabinets.get(cabinet_id=cabinet_id)
                door_closed = status_data['door']
                cabinet.lock_angle = status_data['lock_angle']
                cabinet.lock_locked = status_data['lock_locked']
                cabinet.has_item = status_data['has_item']

                # 柜门关闭时锁定，开启时解锁
                cabinet.is_locked = not door_closed

                # 更新物品检测时间
                if cabinet.has_item is not None:
                    from django.utils import timezone
                    cabinet.item_detected_at = timezone.now()

                cabinet.save()
            except Exception as e:
                # 记录错误日志
                DeviceLog.objects.create(
                    device=device,
                    log_type='error',
                    message=f'更新柜子状态失败: {str(e)}',
                    data={'cabinet_id': cabinet_id, 'status_data': status_data}
                )

        # 更新电量
        battery_level = serializer.validated_data.get('battery_level')
        if battery_level is not None:
            device.battery_level = battery_level
        device.last_heartbeat = timezone.now()
        device.status = 'online'
        device.save()

        # 记录日志
        DeviceLog.objects.create(
            device=device,
            log_type='status',
            message='状态上报',
            data={'cabinet_status': cabinet_status, 'battery_level': battery_level}
        )

        return Response({
            'code': 0,
            'message': '状态更新成功'
        })


@method_decorator(csrf_exempt, name='dispatch')
class DeviceOpenCabinetView(APIView):
    """开柜指令接口（供ESP32轮询获取）"""
    permission_classes = [AllowAny]

    def get(self, request, device_id):
        """ESP32 轮询此接口获取待执行的指令"""
        # 获取并验证API密钥（可选，支持向后兼容）
        api_key = request.headers.get('X-API-Key') or request.data.get('api_key')

        try:
            device = Device.objects.get(device_id=device_id)
            # 验证API密钥（如果提供了）
            if api_key and device.api_key != api_key:
                return Response({
                    'code': 401,
                    'message': 'API密钥验证失败'
                }, status=status.HTTP_401_UNAUTHORIZED)
        except Device.DoesNotExist:
            return Response({
                'code': 404,
                'message': '设备不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        # 检查是否有待执行的开柜指令
        pending_commands = DeviceLog.objects.filter(
            device=device,
            log_type='open',
            created_at__gte=device.last_heartbeat or timezone.now() - timezone.timedelta(minutes=1)
        ).order_by('-created_at')[:1]

        if pending_commands:
            cmd = pending_commands[0]
            return Response({
                'code': 0,
                'message': '有待执行指令',
                'data': {
                    'command': 'open_cabinet',
                    'cabinet_id': cmd.data.get('cabinet_id'),
                    'timestamp': cmd.created_at.isoformat()
                }
            })

        return Response({
            'code': 0,
            'message': '无待执行指令',
            'data': {'command': 'none'}
        })

    def post(self, request, device_id):
        """后端发送开柜指令到设备（通过WebSocket或轮询机制）"""
        api_key = request.headers.get('X-API-Key') or request.data.get('api_key')

        try:
            device = Device.objects.get(device_id=device_id, is_active=True)
        except Device.DoesNotExist:
            return Response({
                'code': 404,
                'message': '设备不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        if api_key and device.api_key != api_key:
            return Response({
                'code': 401,
                'message': 'API密钥验证失败'
            }, status=status.HTTP_401_UNAUTHORIZED)

        serializer = OpenCabinetSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'code': 400,
                'message': '参数错误',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        cabinet_id = serializer.validated_data['cabinet_id']
        pickup_code = serializer.validated_data['pickup_code']

        # 验证订单
        from apps.orders.models import Order
        try:
            order = Order.objects.get(
                cabinet__cabinet_id=cabinet_id,
                pickup_code=pickup_code,
                status__in=['paid', 'in_use']
            )
        except Order.DoesNotExist:
            return Response({
                'code': 400,
                'message': '无效的取件码或订单已过期'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 记录开柜指令（ESP32轮询获取）
        DeviceLog.objects.create(
            device=device,
            log_type='open',
            message=f'开柜指令: {cabinet_id}',
            data={'cabinet_id': cabinet_id, 'pickup_code': pickup_code, 'order_id': order.id}
        )

        return Response({
            'code': 0,
            'message': '开柜指令已下发',
            'data': {
                'cabinet_id': cabinet_id,
                'action': 'open'
            }
        })


@method_decorator(csrf_exempt, name='dispatch')
class OpenCabinetByCodeView(APIView):
    """扫码开柜（用户端调用）"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """用户扫描柜子二维码，验证取件码后开柜"""
        serializer = OpenCabinetSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'code': 400,
                'message': '参数错误',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        cabinet_id = serializer.validated_data['cabinet_id']
        pickup_code = serializer.validated_data['pickup_code']

        # 验证柜子是否存在
        from apps.cabinets.models import Cabinet
        try:
            cabinet = Cabinet.objects.get(cabinet_id=cabinet_id)
        except Cabinet.DoesNotExist:
            return Response({
                'code': 404,
                'message': '柜子不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        # 验证订单
        from apps.orders.models import Order
        try:
            order = Order.objects.get(
                cabinet=cabinet,
                pickup_code=pickup_code,
                status__in=['paid', 'in_use']
            )
        except Order.DoesNotExist:
            return Response({
                'code': 400,
                'message': '无效的取件码或订单已过期'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 获取绑定设备
        device = cabinet.devices.first()
        if not device:
            return Response({
                'code': 500,
                'message': '柜子未绑定设备'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 记录开柜指令
        DeviceLog.objects.create(
            device=device,
            log_type='open',
            message=f'用户开柜: {cabinet_id}',
            data={'cabinet_id': cabinet_id, 'pickup_code': pickup_code, 'order_id': order.id}
        )

        # 更新订单状态
        if order.status == 'paid':
            order.status = 'in_use'
            order.save()

        # 更新柜子状态
        cabinet.is_locked = False
        cabinet.status = 'in_use'
        cabinet.save()

        return Response({
            'code': 0,
            'message': '开柜成功',
            'data': {
                'cabinet_id': cabinet_id,
                'action': 'open',
                'order_id': order.id
            }
        })


# ============================================
# 设备管理接口（需要管理员认证）
# ============================================

class DeviceViewSet(viewsets.ModelViewSet):
    """设备管理视图集"""
    queryset = Device.objects.all()
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == 'list':
            return DeviceListSerializer
        return DeviceSerializer

    def get_queryset(self):
        queryset = Device.objects.all()

        # 筛选站点
        station = self.request.query_params.get('station')
        if station:
            queryset = queryset.filter(station=station)

        # 筛选状态
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    def perform_create(self, serializer):
        # 自动生成API密钥
        if not serializer.validated_data.get('api_key'):
            serializer.save(api_key=str(uuid.uuid4()).replace('-', ''))
        else:
            serializer.save()


class DeviceLogsView(APIView):
    """设备日志查询"""
    permission_classes = [IsAdminUser]

    def get(self, request, device_id):
        try:
            device = Device.objects.get(device_id=device_id)
        except Device.DoesNotExist:
            return Response({
                'code': 404,
                'message': '设备不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        logs = DeviceLog.objects.filter(device=device)[:100]
        serializer = DeviceLogSerializer(logs, many=True)
        return Response({
            'code': 0,
            'message': 'success',
            'data': serializer.data
        })


@method_decorator(csrf_exempt, name='dispatch')
class DeviceStatusQueryView(APIView):
    """服务器主动查询柜子状态（ESP32响应）"""
    permission_classes = [AllowAny]

    def get(self, request, device_id):
        """ESP32 轮询获取服务器下发的状态查询指令"""
        # 获取并验证API密钥（可选，支持向后兼容）
        api_key = request.headers.get('X-API-Key') or request.data.get('api_key')

        try:
            device = Device.objects.get(device_id=device_id)
            # 验证API密钥（如果提供了）
            if api_key and device.api_key != api_key:
                return Response({
                    'code': 401,
                    'message': 'API密钥验证失败'
                }, status=status.HTTP_401_UNAUTHORIZED)
        except Device.DoesNotExist:
            return Response({
                'code': 404,
                'message': '设备不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        # 检查是否有待执行的查询指令
        pending_query = DeviceLog.objects.filter(
            device=device,
            log_type='status_query',
            created_at__gte=device.last_heartbeat or timezone.now() - timezone.timedelta(minutes=1)
        ).order_by('-created_at')[:1]

        if pending_query:
            query_log = pending_query[0]
            # 返回需要查询的柜子ID列表
            cabinet_ids = query_log.data.get('cabinet_ids', [])
            return Response({
                'code': 0,
                'message': '有待查询指令',
                'data': {
                    'command': 'query_status',
                    'cabinet_ids': cabinet_ids,
                    'timestamp': query_log.created_at.isoformat()
                }
            })

        return Response({
            'code': 0,
            'message': '无待执行指令',
            'data': {'command': 'none'}
        })


class CabinetStatusQueryView(APIView):
    """服务器主动查询柜子状态（管理员调用）"""
    permission_classes = [IsAdminUser]

    def get(self, request, device_id):
        """查询指定设备的柜子状态"""
        try:
            device = Device.objects.get(device_id=device_id)
        except Device.DoesNotExist:
            return Response({
                'code': 404,
                'message': '设备不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        # 检查设备是否在线
        if not device.is_online():
            return Response({
                'code': 400,
                'message': '设备离线，无法查询'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 获取绑定柜子ID列表
        cabinet_ids = list(device.bound_cabinets.values_list('cabinet_id', flat=True))

        # 记录查询指令（ESP32轮询获取）
        DeviceLog.objects.create(
            device=device,
            log_type='status_query',
            message=f'服务器查询柜子状态',
            data={'cabinet_ids': cabinet_ids, 'query_time': timezone.now().isoformat()}
        )

        # 等待 ESP32 上报状态（这里返回已记录的本地状态）
        from apps.cabinets.models import Cabinet
        cabinets = device.bound_cabinets.all()
        cabinet_data = []
        for cabinet in cabinets:
            cabinet_data.append({
                'cabinet_id': cabinet.cabinet_id,
                'door_closed': not cabinet.is_locked,
                'lock_angle': cabinet.lock_angle,
                'lock_locked': cabinet.lock_locked,
                'has_item': cabinet.has_item,
                'item_detected_at': cabinet.item_detected_at.isoformat() if cabinet.item_detected_at else None,
                'last_updated': cabinet.updated_at.isoformat()
            })

        return Response({
            'code': 0,
            'message': '查询指令已下发，请等待设备响应',
            'data': {
                'device_id': device.device_id,
                'status': device.status,
                'last_heartbeat': device.last_heartbeat.isoformat() if device.last_heartbeat else None,
                'cabinets': cabinet_data
            }
        })
