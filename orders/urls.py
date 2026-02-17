from django.urls import path
from . import views

urlpatterns = [
    path("", views.my_orders, name="orders_home"),
    path("checkout/", views.checkout, name="checkout"),
    # path("my-orders/", views.my_orders, name="my_orders"),
    path('', views.my_orders, name='my_orders'),
    path("order-success/", views.order_success, name="order_success"),
    path('dashboard/', views.dashboard, name='dashboard'),
    


]
