from django.urls import path
from .views import CabinetListView, CabinetDetailView, CabinetStatusView, AvailableCabinetsView, CabinetCreateView

urlpatterns = [
    path('', CabinetListView.as_view(), name='cabinet-list'),
    path('available/', AvailableCabinetsView.as_view(), name='available-cabinets'),
    path('create/', CabinetCreateView.as_view(), name='cabinet-create'),
    path('<str:cabinet_id>/', CabinetDetailView.as_view(), name='cabinet-detail'),
    path('<str:cabinet_id>/status/', CabinetStatusView.as_view(), name='cabinet-status'),
]
