from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from decimal import Decimal

from .models import Product, Profile, Category, WishlistItem, Cart, CartItem, Order, OrderItem, Payment
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import razorpay

# --------------------------
# Home page
# --------------------------
def home(request):
    categories = Category.objects.all()
    cart = request.session.get('cart', {})
    cart_count = sum(cart.values()) if isinstance(cart, dict) else 0
    wishlist_ids = set()
    if request.user.is_authenticated:
        wishlist_ids = set(WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True))
    return render(request, 'shop/index.html', {
        'categories': categories,
        'cart_count': cart_count,
        'wishlist_ids': wishlist_ids,
    })

# --------------------------
# All Products page
# --------------------------
def all_products(request):
    return redirect('home')

# --------------------------
# Categories page
# --------------------------
def categories(request):
    categories = Category.objects.all()
    return render(request, 'shop/categories.html', {'categories': categories})

# --------------------------
# Products filtered by category
# --------------------------
def products_by_category(request, category_slug):
    return redirect('home')

# --------------------------
# Profile page
# --------------------------
@login_required(login_url='login')
def profile_view(request):
    profile = getattr(request.user, 'profile', None)
    return render(request, 'shop/profile.html', {
        'user': request.user,
        'profile': profile,
    })

# --------------------------
# Signup view
# --------------------------
def signup(request):
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        email = (request.POST.get('email') or '').strip()
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if not username or not email or not password:
            messages.error(request, "All fields are required!")
            return redirect('signup')

        if password != password2:
            messages.error(request, "Passwords do not match!")
            return redirect('signup')

        try:
            validate_password(password)
        except ValidationError as e:
            for error in e:
                messages.error(request, error)
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect('signup')

        with transaction.atomic():
            user = User.objects.create_user(username=username, email=email, password=password)

        login(request, user)
        messages.success(request, f"Welcome {user.username}! Your account has been created.")
        return redirect('home')

    return render(request, 'shop/signup.html')

# --------------------------
# Login view
# --------------------------
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next') or 'home'
            return redirect(next_url)
        else:
            messages.error(request, "⚠️ Invalid username or password!")
            return render(request, 'shop/login.html', {'username': username})

    return render(request, 'shop/login.html')

# --------------------------
# Logout view
# --------------------------
@login_required(login_url='login')
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, "You have been logged out successfully.")
        return redirect('home')
    return redirect('home')

# --------------------------
# Edit Profile view
# --------------------------
@login_required(login_url='login')
def edit_profile_view(request):
    user = request.user
    profile = getattr(user, 'profile', None)

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        mobile_number = request.POST.get('mobile_number', '').strip()
        address = request.POST.get('address', '').strip()

        user.first_name = first_name or user.first_name
        user.last_name = last_name or user.last_name
        if email:
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                messages.error(request, "This email is already taken by another account!")
                return redirect('edit_profile')
            user.email = email
        user.save()

        if profile:
            profile.mobile_number = mobile_number or profile.mobile_number
            profile.address = address or profile.address
            profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('profile')

    return render(request, 'shop/edit_profile.html', {
        'user': user,
        'profile': profile
    })

# --------------------------
# Dashboard view
# --------------------------
@login_required(login_url='login')
def dashboard(request):
    return render(request, 'shop/dashboard.html')

# --------------------------
# Product Detail view
# --------------------------
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shop/product_detail.html', {'product': product})

# --------------------------
# Standalone Buy form (no product context)
# --------------------------
@login_required(login_url='login')
def buy_form(request):
    # Render the confirm order form without a specific product
    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        phone = (request.POST.get('phone') or '').strip()
        address = (request.POST.get('address') or '').strip()
        payment_method = (request.POST.get('payment_method') or 'cod')
        profile = getattr(request.user, 'profile', None)
        if profile:
            order = Order.objects.create(customer=profile)
            if payment_method == 'upi':
                return redirect('pay_now', order_id=order.id)
            messages.success(request, "Order placed successfully.")
            return redirect('order_success', order_id=order.id)
        messages.success(request, "Order info received.")
        return redirect('home')
    # Reuse the buy_now template with minimal context
    return render(request, 'shop/buy_now.html', {'product': None})

# --------------------------
# Billing page (standalone, user-facing)
# --------------------------
@login_required(login_url='login')
def billing_page(request):
    if request.method == 'POST':
        # In a real app, validate and create an order; for now just ack and go home
        messages.success(request, "Billing details submitted. We'll process your order.")
        return redirect('home')
    return render(request, 'shop/billing.html', { 'hide_navbar': True })

# --------------------------
# Static info pages for top bar
# --------------------------
def support_page(request):
    return render(request, 'shop/support.html')

def returns_page(request):
    return render(request, 'shop/returns.html')

def track_order_page(request):
    return render(request, 'shop/track_order.html')

def offers_page(request):
    categories = Category.objects.all()
    products = Product.objects.order_by('-discount').all()[:24]
    return render(request, 'shop/offers.html', { 'categories': categories, 'products': products })

# --------------------------
# About page
# --------------------------
def about(request):
    return render(request, 'shop/about.html')

# --------------------------
# Contact page
# --------------------------
def contact(request):
    return render(request, 'shop/contact.html')

def order_success(request, order_id):
    return render(request, 'shop/order_success.html', { 'order_id': order_id })

@login_required(login_url='login')
def my_orders(request):
    profile = getattr(request.user, 'profile', None)
    orders = Order.objects.filter(customer=profile).order_by('-created_at') if profile else []
    return render(request, 'shop/my_orders.html', { 'orders': orders })

# --------------------------
# Buy Now view
# --------------------------
@login_required(login_url='login')
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    profile, _ = Profile.objects.get_or_create(user=request.user)

    # --- Handle POST request (when user submits the form) ---
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1

        # If the user is placing the final order
        if 'payment_method' in request.POST:
            name = request.POST.get('name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            payment_method = request.POST.get('payment_method')

            # Update profile for future use
            profile.address = address
            profile.mobile_number = phone
            profile.save()

            # Recalculate total for order creation
            subtotal = product.discounted_price() * quantity
            cgst = round(subtotal * Decimal('0.09'), 2)
            sgst = round(subtotal * Decimal('0.09'), 2)
            delivery_charge = Decimal('50.00')
            packaging_charge = Decimal('20.00')
            handling_charge = Decimal('15.00')
            grand_total = subtotal + cgst + sgst + delivery_charge + packaging_charge + handling_charge

            order = Order.objects.create(
                customer=profile,
                user=request.user,
                shipping_address=address,
                total_amount=grand_total,
                payment_method=payment_method,
                payment_status='Pending'
            )
            OrderItem.objects.create(order=order, product=product, quantity=quantity)

            messages.success(request, "Your order has been placed successfully!")
            if payment_method == 'upi':
                return redirect('pay_now', order_id=order.id)
            else:
                # Assuming you have an order success page
                return redirect('home') # Or redirect to an order success page

    # --- Handle GET request (when page first loads) or quantity change ---
    # This block now runs for the initial page load and when quantity is updated.
    quantity = int(request.GET.get('quantity', 1))
    if quantity < 1:
        quantity = 1

    # --- Perform Billing Calculations ---
    subtotal = product.discounted_price() * quantity
    cgst = round(subtotal * Decimal('0.09'), 2)
    sgst = round(subtotal * Decimal('0.09'), 2)
    delivery_charge = Decimal('50.00')
    packaging_charge = Decimal('20.00')
    handling_charge = Decimal('15.00')
    grand_total = subtotal + cgst + sgst + delivery_charge + packaging_charge + handling_charge

    # --- Prepare Context for Template ---
    total_gst = cgst + sgst
    base_price = product.discounted_price()
    context = {
        'product': product,
        'profile': profile,
        'quantity': quantity,
        'subtotal': subtotal,
        'cgst': cgst,
        'sgst': sgst,
        'total_gst': total_gst,
        'delivery_charge': delivery_charge,
        'packaging_charge': packaging_charge,
        'handling_charge': handling_charge,
        'grand_total': grand_total,
        'base_price': base_price,
    }

    return render(request, 'shop/buy_now.html', context)

# --------------------------
# Payments (Razorpay)
# --------------------------
@login_required(login_url='login')
def payment_create(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    # Ensure order has items; if not, try to hydrate from user's cart
    if order.items.count() == 0 and request.user.is_authenticated:
        cart_obj, _ = Cart.objects.get_or_create(user=request.user)
        for ci in cart_obj.items.select_related('product').all():
            OrderItem.objects.get_or_create(order=order, product=ci.product, defaults={'quantity': ci.quantity})

    # Check if Razorpay keys are configured
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        return JsonResponse({
            'ok': False, 
            'message': 'Payment gateway not configured. Please contact administrator.'
        }, status=400)

    amount_rupees = max(int(order.total_amount), 1)
    amount_paise = amount_rupees * 100
    
    try:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        rp_order = client.order.create(dict(
            amount=amount_paise, 
            currency='INR', 
            payment_capture=1
        ))
        
        Payment.objects.create(
            order=order, 
            razorpay_order_id=rp_order['id'], 
            amount=amount_rupees, 
            status=rp_order.get('status', 'created')
        )
        
        data = {
            'ok': True,
            'key': settings.RAZORPAY_KEY_ID,
            'amount': amount_paise,
            'currency': 'INR',
            'name': 'Furniture Shop',
            'description': f'Order #{order.id}',
            'order_id': rp_order['id'],
            'prefill': {
                'name': request.user.get_full_name() or request.user.username, 
                'email': request.user.email or ''
            },
            'notes': {'order_id': str(order.id)},
            'theme': {'color': '#b57a50'}
        }
        return JsonResponse(data)
    except razorpay.errors.BadRequestError as e:
        return JsonResponse({
            'ok': False, 
            'message': 'Invalid payment request. Please try again.',
            'detail': str(e)[:200]
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'ok': False, 
            'message': 'Payment gateway error. Please try again later.',
            'detail': str(e)[:200]
        }, status=500)

@csrf_exempt
def payment_verify(request):
    """Verify Razorpay payment signature"""
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'message': 'Invalid request method'}, status=400)
    
    payload = request.POST
    rp_order_id = payload.get('razorpay_order_id')
    rp_payment_id = payload.get('razorpay_payment_id')
    rp_signature = payload.get('razorpay_signature')
    
    # Validate required fields
    if not all([rp_order_id, rp_payment_id, rp_signature]):
        return JsonResponse({
            'ok': False, 
            'message': 'Missing payment details'
        }, status=400)
    
    # Check if Razorpay keys are configured
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        return JsonResponse({
            'ok': False, 
            'message': 'Payment gateway not configured'
        }, status=400)
    
    try:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        client.utility.verify_payment_signature({
            'razorpay_order_id': rp_order_id,
            'razorpay_payment_id': rp_payment_id,
            'razorpay_signature': rp_signature
        })
    except razorpay.errors.SignatureVerificationError:
        # Update payment status to failed
        Payment.objects.filter(razorpay_order_id=rp_order_id).update(
            razorpay_payment_id=rp_payment_id, 
            razorpay_signature=rp_signature, 
            status='failed'
        )
        return JsonResponse({'ok': False, 'message': 'Payment verification failed'}, status=400)
    except Exception as e:
        return JsonResponse({
            'ok': False, 
            'message': 'Verification error',
            'detail': str(e)[:200]
        }, status=500)
    
    # Find and update payment
    payment = Payment.objects.filter(razorpay_order_id=rp_order_id).select_related('order').first()
    if not payment:
        return JsonResponse({'ok': False, 'message': 'Payment record not found'}, status=404)
    
    # Update payment and order status
    payment.razorpay_payment_id = rp_payment_id
    payment.razorpay_signature = rp_signature
    payment.status = 'paid'
    payment.save()
    
    payment.order.payment_status = 'Paid'
    payment.order.save()
    
    return JsonResponse({'ok': True, 'message': 'Payment verified successfully'})

@login_required(login_url='login')
def pay_now(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # If already paid, redirect to success
    if order.payment_status == 'Paid':
        return redirect('order_success', order_id=order.id)

    # If order has no items, populate from cart
    if order.items.count() == 0:
        cart_obj, _ = Cart.objects.get_or_create(user=request.user)
        for ci in cart_obj.items.select_related('product').all():
            OrderItem.objects.get_or_create(
                order=order,
                product=ci.product,
                defaults={'quantity': ci.quantity}
            )

    # Calculate billing
    subtotal = sum(item.product.price * item.quantity for item in order.items.all())
    tax = round(subtotal * 0.18, 2)  # GST 18%
    delivery = 50 if subtotal > 0 else 0  # Optional: free delivery if subtotal > certain amount
    total = round(subtotal + tax + delivery, 2)

    # Update order total
    order.total_amount = total
    order.save()

    context = {
        'order': order,
        'order_items': order.items.all(),
        'subtotal': subtotal,
        'tax': tax,
        'delivery': delivery,
        'total': total
    }

    return render(request, 'pay_now.html', context)

# --------------------------
# Add to Cart
# --------------------------
@login_required(login_url='login')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Ensure user cart exists in DB
    cart_obj, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart_obj, product=product)
    if not created:
        item.quantity += 1
        item.save()

    # Mirror to session for quick count display
    session_cart = request.session.get('cart', {})
    session_cart[str(product.id)] = item.quantity
    request.session['cart'] = session_cart

    messages.success(request, f"{product.name} added to cart!")
    return redirect('cart')

# --------------------------
# View Cart
# --------------------------
@login_required(login_url='login')
def cart_view(request):
    cart_obj, _ = Cart.objects.get_or_create(user=request.user)
    items = cart_obj.items.select_related('product').all()
    products = []
    total = 0
    for item in items:
        product = item.product
        product.qty = item.quantity
        product.total_price = product.price * item.quantity
        products.append(product)
        total += product.total_price

    # sync session count for header
    request.session['cart'] = {str(i.product.id): i.quantity for i in items}

    return render(request, 'shop/cart.html', {'products': products, 'total': total})

# --------------------------
# Remove from Cart
# --------------------------
@login_required(login_url='login')
def remove_from_cart(request, product_id):
    cart_obj, _ = Cart.objects.get_or_create(user=request.user)
    try:
        item = cart_obj.items.select_related('product').get(product_id=product_id)
        item.delete()
        # sync session count for header
        request.session['cart'] = {str(i.product.id): i.quantity for i in cart_obj.items.all()}
        messages.success(request, "Item removed from cart.")
    except CartItem.DoesNotExist:
        messages.error(request, "Item not found in your cart.")
    return redirect('cart')

# --------------------------
# Wishlist View
# --------------------------
@login_required(login_url='login')
def wishlist_view(request):
    items = WishlistItem.objects.filter(user=request.user).select_related('product')
    products = [wi.product for wi in items]
    return render(request, 'shop/wishlist.html', { 'products': products })

@login_required(login_url='login')
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wi, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        wi.delete()
        status = 'removed'
    else:
        status = 'added'
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': status})
    messages.success(request, f"Wishlist {status} for {product.name}")
    return redirect('all_products')

# Aliases with requested names
@login_required(login_url='login')
def wishlist_toggle(request, product_id):
    return toggle_wishlist(request, product_id)

@login_required(login_url='login')
def wishlist_page(request):
    return wishlist_view(request)
