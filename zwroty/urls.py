from django.urls import path
from .views import (
    ReturnOrderCreate, 
    HomeView, AddProduct, 
    AddLineMenuView, 
    ReportWZView,
    OrderStorageView
    )

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path(
        "return-order-create/", ReturnOrderCreate.as_view(), name="create_return_order"
    ),
    path("add-line-search/", AddLineMenuView.as_view(), name="add_line_menu"),
    path("add-product", AddProduct.as_view(), name="add_product"),
    path("report-wz", ReportWZView.as_view(), name="report_wz"),
    path("order-storage", OrderStorageView.as_view(), name="order_filter_page"),
]

app_name = "zwroty"
