from django.urls import path
from .views import ReturnOrderCreate, HomeView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("return-order-create/", ReturnOrderCreate.as_view(),  name="create_return_order"),
]

app_name = "zwroty"