from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from orders.models import Order
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! You can login now.")
            return redirect("login")
    else:
        form = UserCreationForm()

    return render(request, "accounts/register.html", {"form": form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect("product_list")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("product_list")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "accounts/login.html")


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("product_list")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("signup")

        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        return redirect("product_list")

    return render(request, "accounts/signup.html")


def logout_view(request):
    logout(request)
    return redirect("product_list")


@login_required
def profile(request):
    user_orders = Order.objects.filter(user=request.user)
    return render(request, 'accounts/profile.html', {'orders': user_orders})

@login_required
def settings_view(request):
    return render(request, 'accounts/settings.html')