from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .models import Product, Order, OrderItem

def home(request):
    products = Product.objects.filter(available=True)
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    if query:
        products = products.filter(name__icontains=query) | products.filter(description__icontains=query)
    if category:
        products = products.filter(category__iexact=category)
    categories = Product.objects.filter(available=True).values_list("category", flat=True).distinct()
    return render(request, "store/home.html", {"products": products.distinct(), "categories": categories, "query": query, "selected_category": category})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, available=True)
    return render(request, "store/product_detail.html", {"product": product})

def _cart_data(request):
    cart_session = request.session.get("cart", {})
    items, total, count = [], Decimal("0.00"), 0
    for key, quantity in cart_session.items():
        try:
            product = Product.objects.get(pk=int(key), available=True)
            quantity = max(1, min(int(quantity), product.stock))
        except (Product.DoesNotExist, ValueError, TypeError):
            continue
        subtotal = product.price * quantity
        items.append({"product": product, "quantity": quantity, "subtotal": subtotal})
        total += subtotal
        count += quantity
    return items, total, count

def cart(request):
    items, total, count = _cart_data(request)
    return render(request, "store/cart.html", {"items": items, "total": total, "cart_count": count})

@require_POST
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk, available=True)
    if product.stock < 1:
        messages.error(request, "This product is out of stock.")
        return redirect("home")
    cart_session = request.session.get("cart", {})
    key = str(product.pk)
    cart_session[key] = min(int(cart_session.get(key, 0)) + 1, product.stock)
    request.session["cart"] = cart_session
    messages.success(request, f"{product.name} added to your cart.")
    return redirect(request.POST.get("next") or "cart")

@require_POST
def update_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart_session = request.session.get("cart", {})
    key = str(pk)
    try:
        quantity = int(request.POST.get("quantity", "1"))
    except ValueError:
        quantity = 1
    if quantity <= 0:
        cart_session.pop(key, None)
    elif product.available and product.stock:
        cart_session[key] = min(quantity, product.stock)
    else:
        cart_session.pop(key, None)
    request.session["cart"] = cart_session
    return redirect("cart")

@require_POST
def remove_from_cart(request, pk):
    cart_session = request.session.get("cart", {})
    cart_session.pop(str(pk), None)
    request.session["cart"] = cart_session
    return redirect("cart")

@login_required
def checkout(request):
    items, total, count = _cart_data(request)
    if not items:
        messages.info(request, "Your cart is empty.")
        return redirect("home")
    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        address = request.POST.get("address", "").strip()
        phone = request.POST.get("phone", "").strip()
        if not full_name or not address or not phone:
            messages.error(request, "Please complete all delivery details.")
            return render(request, "store/checkout.html", {"items": items, "total": total})
        with transaction.atomic():
            # Recheck stock before creating the order.
            for item in items:
                product = Product.objects.select_for_update().get(pk=item["product"].pk)
                if not product.available or product.stock < item["quantity"]:
                    messages.error(request, f"Insufficient stock for {product.name}. Please update your cart.")
                    return redirect("cart")
            order = Order.objects.create(user=request.user, full_name=full_name, address=address, phone=phone, total=total)
            for item in items:
                product = Product.objects.get(pk=item["product"].pk)
                OrderItem.objects.create(order=order, product=product, product_name=product.name, price=product.price, quantity=item["quantity"])
                product.stock -= item["quantity"]
                product.save(update_fields=["stock"])
        request.session["cart"] = {}
        messages.success(request, f"Order #{order.pk} placed successfully.")
        return redirect("order_history")
    return render(request, "store/checkout.html", {"items": items, "total": total})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related("items")
    return render(request, "store/order_history.html", {"orders": orders})

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your account has been created.")
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "store/register.html", {"form": form})
