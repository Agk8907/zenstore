from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Avg
from django.conf import settings
from django.core.mail import send_mail
import json
import datetime
# import razorpay  <-- Removed to prevent import errors if not installed/configured
from .models import *
from django.contrib.auth.decorators import login_required
from .forms import CreateUserForm, UserLoginForm
from django.contrib.auth import login, logout
from django.contrib import messages

# --- HELPER ---
def get_cart_data(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(user=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []; order = {'get_cart_total':0, 'get_cart_items':0}; cartItems = 0
    return {'items':items, 'order':order, 'cartItems':cartItems}

# --- MOCK PAYMENT LOGIC (Simulates Server Processing) ---
def initiate_payment(request):
    # Just returns success to open the modal
    return JsonResponse({'status': 'ready'})

def verify_payment(request):
    # This replaces the Razorpay verification
    if request.method == 'POST':
        try:
            customer = request.user
            order = Order.objects.get(user=customer, complete=False)
            
            # 1. Complete Order
            order.complete = True
            # Generate a Fake Transaction ID
            order.transaction_id = "TXN-" + str(datetime.datetime.now().timestamp()).replace('.', '')
            order.save()

            # 2. Decrement Stock
            items = order.orderitem_set.all()
            for item in items:
                item.product.stock -= item.quantity
                item.product.save()

            # 3. Send Email (Still Real!)
            try:
                subject = f"Order Confirmed! #{order.id}"
                message = f"Hi {customer.first_name},\n\nThank you for your order!\nTotal: ₹{order.get_cart_total}\nTransaction ID: {order.transaction_id}\n\nYour items will be shipped soon."
                send_mail(subject, message, settings.EMAIL_HOST_USER, [customer.email], fail_silently=True)
            except Exception as e:
                print(f"Email Error (Check settings.py): {e}")

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error'})

# --- STANDARD VIEWS (Unchanged) ---
def home(request):
    data = get_cart_data(request)
    categories = Category.objects.all()
    return render(request, 'store/home.html', {'categories': categories, 'cartItems': data['cartItems']})

def products(request):
    data = get_cart_data(request)
    products = Product.objects.annotate(avg_rating=Avg('review__rating'))
    categories = Category.objects.all()
    category_id = request.GET.get('category'); min_price = request.GET.get('min_price'); max_price = request.GET.get('max_price'); rating_filter = request.GET.get('rating')
    if category_id and category_id != '': products = products.filter(category_id=category_id)
    if min_price: products = products.filter(price__gte=min_price)
    if max_price: products = products.filter(price__lte=max_price)
    if rating_filter: products = products.filter(avg_rating__gte=rating_filter)
    if request.user.is_authenticated:
        wishlist_ids = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
        for p in products: p.is_wishlisted = p.id in wishlist_ids
    context = {'products': products, 'categories': categories, 'active_category': category_id, 'cartItems': data['cartItems'], 'active_min': min_price, 'active_max': max_price, 'active_rating': rating_filter}
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' or request.GET.get('ajax') == 'true':
        return render(request, 'store/product_list_partial.html', context)
    return render(request, 'store/products.html', context)

def product_detail(request, pk):
    data = get_cart_data(request)
    product = get_object_or_404(Product, id=pk)
    reviews = Review.objects.filter(product=product).order_by('-created_at')
    has_purchased = False; is_wishlisted = False
    if request.user.is_authenticated:
        has_purchased = Order.objects.filter(user=request.user, complete=True, orderitem__product=product).exists()
        is_wishlisted = Wishlist.objects.filter(user=request.user, product=product).exists()
    if request.method == 'POST' and request.user.is_authenticated:
        Review.objects.create(user=request.user, product=product, rating=request.POST.get('rating'), comment=request.POST.get('comment'))
        return redirect('product_detail', pk=pk)
    return render(request, 'store/product_detail.html', {'product': product, 'reviews': reviews, 'has_purchased': has_purchased, 'is_wishlisted': is_wishlisted, 'cartItems': data['cartItems']})

def cart(request):
    data = get_cart_data(request)
    return render(request, 'store/cart.html', {'items':data['items'], 'order':data['order'], 'cartItems': data['cartItems']})

@login_required(login_url='login')
def checkout(request):
    data = get_cart_data(request)
    if data['order'].get_cart_items == 0: return redirect('products')
    if request.method == 'POST':
        u = request.user
        u.first_name=request.POST.get('first_name'); u.last_name=request.POST.get('last_name')
        u.address=request.POST.get('address'); u.city=request.POST.get('city'); u.zipcode=request.POST.get('zipcode'); u.phone_number=request.POST.get('phone')
        u.save()
        return redirect('payment')
    return render(request, 'store/checkout.html', {'items':data['items'], 'order':data['order'], 'cartItems': data['cartItems']})

@login_required(login_url='login')
def payment(request):
    data = get_cart_data(request)
    if data['order'].get_cart_items == 0: return redirect('products')
    if not request.user.address: messages.error(request, "Please enter shipping address"); return redirect('checkout')
    # No Razorpay keys needed here anymore
    return render(request, 'store/payment.html', {'items':data['items'], 'order':data['order'], 'cartItems': data['cartItems']})

def updateItem(request):
    try: data = json.loads(request.body); productId = data['productId']; action = data['action']; quantity = int(data.get('quantity', 1))
    except: return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)
    if request.user.is_authenticated:
        customer = request.user
        try: product = Product.objects.get(id=productId)
        except: return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)
        order, created = Order.objects.get_or_create(user=customer, complete=False)
        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
        if action == 'add':
            if (orderItem.quantity + quantity) <= product.stock: orderItem.quantity += quantity
            else: return JsonResponse({'status': 'error', 'message': 'Not enough stock!'}, status=400)
        elif action == 'remove': orderItem.quantity -= 1
        orderItem.save()
        if orderItem.quantity <= 0: orderItem.delete()
        return JsonResponse({'status': 'success', 'cartTotal': order.get_cart_items}, safe=False)
    return JsonResponse({'status': 'error', 'message': 'Please login'}, status=403)

# Only kept to avoid URL errors, not used logic
def process_order(request): return JsonResponse({'status':'error'}, safe=False)

@login_required(login_url='login')
def profile(request):
    data = get_cart_data(request)
    if request.method == 'POST':
        u = request.user; u.first_name=request.POST.get('first_name'); u.last_name=request.POST.get('last_name');
        u.phone_number=request.POST.get('phone_number'); u.address=request.POST.get('address');
        u.city=request.POST.get('city'); u.zipcode=request.POST.get('zipcode'); u.save()
        messages.success(request, "Profile Updated")
    orders = Order.objects.filter(user=request.user, complete=True).order_by('-date_ordered')
    return render(request, 'store/profile.html', {'orders': orders, 'cartItems': data['cartItems']})

@login_required(login_url='login')
def toggle_wishlist(request):
    data = json.loads(request.body); product = Product.objects.get(id=data['productId'])
    item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created: item.delete(); status='removed'
    else: status='added'
    return JsonResponse({'status': status})

@login_required(login_url='login')
def wishlist_view(request):
    data = get_cart_data(request); wishlist_items = Wishlist.objects.filter(user=request.user)
    products = [item.product for item in wishlist_items]
    for p in products: p.is_wishlisted = True
    return render(request, 'store/wishlist.html', {'products': products, 'cartItems': data['cartItems']})

def products_partial(request): 
    products = Product.objects.annotate(avg_rating=Avg('review__rating'))
    category_id = request.GET.get('category'); min_price = request.GET.get('min_price'); max_price = request.GET.get('max_price'); rating_filter = request.GET.get('rating')
    if category_id and category_id != '': products = products.filter(category_id=category_id)
    if min_price: products = products.filter(price__gte=min_price)
    if max_price: products = products.filter(price__lte=max_price)
    if rating_filter: products = products.filter(avg_rating__gte=rating_filter)
    return render(request, 'store/product_list_partial.html', {'products': products})

def registerPage(request):
    if request.user.is_authenticated: return redirect('home')
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid(): user = form.save(); login(request, user); return redirect('home')
    return render(request, 'store/register.html', {'form': form})

def loginPage(request):
    if request.user.is_authenticated: return redirect('home')
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid(): login(request, form.get_user()); return redirect('home')
        else: messages.error(request, 'Invalid credentials')
    return render(request, 'store/login.html', {'form': UserLoginForm()})

def logoutUser(request): logout(request); return redirect('login')

from django.http import HttpResponse
from django.contrib.auth import get_user_model

