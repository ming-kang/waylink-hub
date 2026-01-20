from django.urls import path
from .views import (
    OrderCreateView, OrderPaymentView, OrderDetailView,
    MyOrdersView, OrderExtendView, OrderCancelView
)

urlpatterns = [
    path('create/', OrderCreateView.as_view(), name='order-create'),
    path('my/', MyOrdersView.as_view(), name='my-orders'),
    path('<int:order_id>/', OrderDetailView.as_view(), name='order-detail'),
    path('<int:order_id>/pay/', OrderPaymentView.as_view(), name='order-payment'),
    path('<int:order_id>/extend/', OrderExtendView.as_view(), name='order-extend'),
    path('<int:order_id>/cancel/', OrderCancelView.as_view(), name='order-cancel'),
]
