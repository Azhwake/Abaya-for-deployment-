from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required,  user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.db.models import Sum, F
from .models import Order, OrderItem
from store.models import Product
from django.utils.timezone import now

# ---------------------------
# Checkout (create order from session cart)
# ---------------------------
def checkout(request):
    cart = request.session.get("cart", {})
    cart_items = []
    total_price = 0

    if not cart:
        return redirect("product_list")

    # Calculate cart items and total
    for product_id, item in cart.items():  # <-- item is a dict
        product = Product.objects.get(id=product_id)
        quantity = item.get("quantity", 0)  # <-- extract the quantity number
        cart_items.append({"product": product, "quantity": quantity})
        total_price += product.price * quantity

    if request.method == "POST":
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            full_name=request.POST.get("full_name", ""),
            email=request.POST.get("email", ""),
            phone_number=request.POST.get("phone", "N/A"),
            address=request.POST.get("address", ""),
            city=request.POST.get("city", ""),
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                price=item["product"].price,
                quantity=item["quantity"],
            )

        # Clear cart
        request.session["cart"] = {}
        return redirect("order_success")

    return render(request, "orders/checkout.html", {"cart": cart_items, "total_price": total_price})


# ---------------------------
# My orders page
# ---------------------------
@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "orders/my_orders.html", {"orders": orders})


# ---------------------------
# Order success page
# ---------------------------
def order_success(request):
    return render(request, "orders/order_success.html")


# ---------------------------
# Admin dashboard
# ---------------------------



def staff_required(user):
    return user.is_staff



@login_required
@user_passes_test(staff_required)
def dashboard(request):
    total_orders = Order.objects.count()
    total_sales = Order.objects.aggregate(
        total=Sum("total_price")
    )["total"] or 0

    orders_today = Order.objects.filter(
        created_at__date=now().date()
    ).count()

    top_products = (
        OrderItem.objects
        .values("product__name")
        .annotate(total_sold=Sum("quantity"))
        .order_by("-total_sold")[:5]
    )

    context = {
        "total_orders": total_orders,
        "total_sales": total_sales,
        "orders_today": orders_today,
        "top_products": top_products,
    }

    return render(request, "dashboard/dashboard.html", context)