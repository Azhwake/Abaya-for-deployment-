from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Product, Category
from orders.models import Order, OrderItem
from .models import BlogPost, NewsletterSubscriber, WishlistItem
from django.contrib import messages
from django.db.models import Q
from django.db.models import Sum, Count
from django.db.models import Sum, F
from django.utils.timezone import now, timedelta
from datetime import datetime


# ----------------------
# Product List & Detail
# ----------------------
def product_list(request):
    products = Product.objects.all().order_by("-id")
    categories = Category.objects.all()

    # Search
    q = request.GET.get("q")
    if q:
        products = products.filter(name__icontains=q)

    # Category filter
    category_slug = request.GET.get("category")
    if category_slug:
        products = products.filter(category__slug=category_slug)

    # Pagination
    paginator = Paginator(products, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"page_obj": page_obj, "categories": categories}
    return render(request, "store/product_list.html", context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, "store/product_detail.html", {"product": product})

# ----------------------
# Cart & Cart Actions
# ----------------------
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    order, created = Order.objects.get_or_create(user=request.user, ordered=False)

    # Pass price in defaults
    order_item, created = OrderItem.objects.get_or_create(
        order=order,
        product=product,
        defaults={'price': product.price}  # <-- fix here
    )

    if not created:
        order_item.quantity += 1
        order_item.save()
    return redirect("cart_detail")


@login_required
def update_cart(request, product_id, action):
    product = get_object_or_404(Product, id=product_id)
    order, created = Order.objects.get_or_create(user=request.user, ordered=False)

    order_item, created = OrderItem.objects.get_or_create(
        order=order,
        product=product,
        defaults={'price': product.price}  # <-- fix here too
    )

    if action == "increase":
        order_item.quantity += 1
        order_item.save()
    elif action == "decrease":
        order_item.quantity -= 1
        if order_item.quantity <= 0:
            order_item.delete()
        else:
            order_item.save()

    return redirect("cart_detail")

@login_required
def cart_detail(request):
    order = Order.objects.filter(user=request.user, ordered=False).first()
    return render(request, "store/cart_detail.html", {"order": order})

# ----------------------
# Checkout
# ----------------------
@login_required
def checkout(request):
    order = Order.objects.filter(user=request.user, ordered=False).first()
    if not order:
        return redirect("product_list")

    if request.method == "POST":
        order.full_name = request.POST.get("full_name")
        order.email = request.POST.get("email")
        order.phone = request.POST.get("phone")
        order.address = request.POST.get("address")
        order.ordered = True
        order.save()

        return redirect("order_success")

    return render(request, "store/checkout.html", {"order": order})

@login_required
def order_success(request):
    return render(request, "store/order_success.html")

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "store/my_orders.html", {"orders": orders})


def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

@login_required
def profile(request):
    return render(request, 'profile.html')


# -------------------------
# Static pages
# -------------------------
def faq(request):
    return render(request, "faq.html")


def returns_policy(request):
    return render(request, "returns_policy.html")


# -------------------------
# Blog / News
# -------------------------
def blog_list(request):
    posts = BlogPost.objects.filter(is_published=True)
    return render(request, "blog_list.html", {"posts": posts})


# -------------------------
# Search products
# -------------------------
def search(request):
    query = request.GET.get("q", "").strip()
    results = []

    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(slug__icontains=query)
        ).distinct()

    context = {
        "query": query,
        "results": results,
        "breadcrumbs": [
            {"label": "Home", "url": "/"},
            {"label": "Search"}
        ]
    }
    return render(request, "search_results.html", context)


# -------------------------
# Newsletter signup (footer form)
# -------------------------
def newsletter_signup(request):
    if request.method != "POST":
        return redirect("product_list")

    email = request.POST.get("email", "").strip().lower()

    if not email:
        messages.error(request, "Please enter your email.")
        return redirect(request.META.get("HTTP_REFERER", "product_list"))

    subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)

    if created:
        messages.success(request, "Welcome ✨ You’re subscribed to our newsletter.")
    else:
        messages.info(request, "You’re already subscribed 💛")

    return redirect(request.META.get("HTTP_REFERER", "product_list"))


# -------------------------
# Wishlist
# -------------------------
@login_required
def wishlist(request):
    items = WishlistItem.objects.filter(user=request.user).select_related("product")

    context = {
        "items": items,
        "breadcrumbs": [
            {"label": "Home", "url": "/"},
            {"label": "Wishlist"}
        ]
    }
    return render(request, "wishlist.html", context)


@login_required
def wishlist_toggle(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    obj = WishlistItem.objects.filter(user=request.user, product=product).first()
    if obj:
        obj.delete()
        messages.info(request, "Removed from wishlist.")
    else:
        WishlistItem.objects.create(user=request.user, product=product)
        messages.success(request, "Added to wishlist ✨")

    return redirect(request.META.get("HTTP_REFERER", "product_list"))

# -------------------------
# Dashboard
# -------------------------

@login_required
def dashboard(request):
    # Total counts
    total_products = Product.objects.count()
    total_orders = Order.objects.count()

    # Total revenue
    total_revenue = OrderItem.objects.filter(order__ordered=True).aggregate(
        total=Sum(F('product__price') * F('quantity'))
    )['total'] or 0

    # Orders over time (last 7 days)
    last_week = now() - timedelta(days=7)
    # Annotate orders by day (use TruncDate to avoid strings)
    from django.db.models.functions import TruncDate

    orders = Order.objects.filter(created_at__gte=last_week).annotate(
        day=TruncDate('created_at')
    ).values('day').annotate(count=Count('id')).order_by('day')

    orders_over_time = {
        "labels": [o['day'].strftime("%b %d") for o in orders],
        "values": [o['count'] for o in orders]
    }

    # Products by category
    categories = Category.objects.annotate(num_products=Count('products'))  # Make sure 'products' matches your related_name
    categories_count = {
        "labels": [c.name for c in categories],
        "values": [c.num_products for c in categories]
    }

    # Recent orders
    recent_orders = Order.objects.order_by('-created_at')[:5]

    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'orders_over_time': orders_over_time,
        'categories_count': categories_count,
        'recent_orders': recent_orders,
    }

    return render(request, 'dashboard/dashboard_base.html', context)