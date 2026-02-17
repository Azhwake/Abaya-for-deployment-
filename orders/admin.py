from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "price", "quantity")

# Main Order admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'full_name', 'email', 'status', 'paid', 'created_at')
    list_filter = ('status', 'paid', 'created_at')
    search_fields = ('full_name', 'email', 'user__username')
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "price", "quantity")
    search_fields = ("order__full_name", "product__name")
