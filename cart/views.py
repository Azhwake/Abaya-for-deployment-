from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product


def cart_detail(request):
    cart = request.session.get("cart", {})
    cart_items = []
    total = 0

    for product_id, item in cart.items():
        product = get_object_or_404(Product, id=product_id)
        quantity = item["quantity"]
        subtotal = product.price * quantity
        total += subtotal

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal,
        })

    return render(request, "store/cart_detail.html", {
        "cart_items": cart_items,
        "total": total,
    })


def add_to_cart(request, product_id):
    cart = request.session.get("cart", {})
    product_id = str(product_id)

    if product_id in cart:
        cart[product_id]["quantity"] += 1
    else:
        cart[product_id] = {"quantity": 1}

    request.session["cart"] = cart
    return redirect("cart_detail")


def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})
    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    request.session["cart"] = cart
    return redirect("cart_detail")


def update_cart(request, product_id, action):
    cart = request.session.get("cart", {})
    product_id = str(product_id)

    if product_id in cart:
        if action == "increase":
            cart[product_id]["quantity"] += 1
        elif action == "decrease":
            cart[product_id]["quantity"] -= 1

            if cart[product_id]["quantity"] <= 0:
                del cart[product_id]

    request.session["cart"] = cart
    return redirect("cart_detail")

