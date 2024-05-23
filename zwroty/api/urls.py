from django.urls import path, include
from .views import WZApiView

urlpatterns = [
    path("wz-order-list/", WZApiView.as_view(), name="wz_order_lis"),
]
