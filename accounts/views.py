from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import AdminRegistrationForm
from .models import AdminProfile

# ----------------------------
# Admin Registration
# ----------------------------
def admin_register(request):
    """
    Handle admin registration
    """
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            # Save user
            user = form.save()

            # Save extra profile data
            phone = form.cleaned_data.get('mobile')
            shop_name = form.cleaned_data.get('shop_name')
            address = form.cleaned_data.get('address')
            admin_role = form.cleaned_data.get('admin_role')
            security_question = form.cleaned_data.get('security_question')

            AdminProfile.objects.create(
                user=user,
                phone=phone,
                shop_name=shop_name,
                address=address,
                admin_role=admin_role,
                security_question=security_question
            )

            # ✅ Auto login user after registration
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Your account has been created.')

            # ✅ Redirect directly to profile page
            return redirect('admin_profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminRegistrationForm()
    
    return render(request, 'accounts/admin_register.html', {'form': form})

# ----------------------------
# Admin Login
# ----------------------------
def admin_login_view(request):
    """
    Handle admin login
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_staff:   # ✅ Ensure only staff/admin can log in here
                login(request, user)
                messages.success(request, f'Welcome {user.username}!')
                return redirect('admin_profile')
            else:
                messages.error(request, 'You are not authorized as an admin.')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/admin_login.html')


# ----------------------------
# Admin Profile
# ----------------------------
@login_required
def admin_profile(request):
    """
    Display admin profile with extra info
    """
    try:
        profile = AdminProfile.objects.get(user=request.user)
    except AdminProfile.DoesNotExist:
        profile = None
        messages.warning(request, 'Profile not found! Please complete your profile.')

    return render(request, 'accounts/admin_profile.html', {'profile': profile})


# ----------------------------
# Admin Logout
# ----------------------------
@login_required
def admin_logout_view(request):
    """
    Logout admin
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('admin_login')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import AdminProfile
from .forms import AdminRegistrationForm  # if you have a separate EditForm, import that instead


@login_required
def edit_profile(request):
    """
    Allow admin to update their profile info
    """
    try:
        profile = AdminProfile.objects.get(user=request.user)
    except AdminProfile.DoesNotExist:
        messages.error(request, "Profile does not exist.")
        return redirect('admin_profile')

    if request.method == 'POST':
        # if you want to use same form as registration
        form = AdminRegistrationForm(request.POST, instance=request.user)
        
        if form.is_valid():
            user = form.save()
            # update profile extra fields
            profile.phone = form.cleaned_data.get('mobile')
            profile.shop_name = form.cleaned_data.get('shop_name')
            profile.save()

            messages.success(request, "Profile updated successfully!")
            return redirect('admin_profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        # Pre-fill with existing data
        form = AdminRegistrationForm(instance=request.user)

    return render(request, 'accounts/edit_profile.html', {'form': form, 'profile': profile})
    from django.shortcuts import render
from shop.models import Category


def all_products(request):
    # Fetch all categories and prefetch products for each
    categories = Category.objects.prefetch_related('products').all()
    return render(request, 'shop/all_products.html', {'categories': categories})
