from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:product_id>/<str:action>/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/', views.order_success, name='order_success'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path("faq/", views.faq, name="faq"),
    path("returns/", views.returns_policy, name="returns_policy"),
    path("news/", views.blog_list, name="blog_list"),
    path("wishlist/", views.wishlist, name="wishlist"),
    path("wishlist/toggle/<int:product_id>/", views.wishlist_toggle, name="wishlist_toggle"),
    path("blog/", views.blog_list, name="blog_list"),
    path("search/", views.search, name="search"),
    path("newsletter/signup/", views.newsletter_signup, name="newsletter_signup"),
    path('dashboard/', views.dashboard, name='dashboard'),
]
