from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Category, Product, Profile, Order, OrderItem, WishlistItem, Cart, CartItem, Payment

# =========================
# CATEGORY ADMIN
# =========================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 20
    prepopulated_fields = {'slug': ('name',)}


# =========================
# PRODUCT ADMIN
# =========================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'category', 'price', 'discount',
        'discounted_price_display', 'rating', 'image_tag', 'slug', 'created_at'
    )
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
    list_per_page = 20
    readonly_fields = ('discounted_price_display', 'image_tag', 'created_at')

    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'category', 'description', 'image', 'image_tag', 'slug')
        }),
        ('Pricing & Rating', {
            'fields': ('price', 'discount', 'discounted_price_display', 'rating')
        }),
    )

    def discounted_price_display(self, obj):
        return f"₹{obj.discounted_price()}"
    discounted_price_display.short_description = 'Discounted Price'

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:50px;"/>', obj.image.url)
        return "-"
    image_tag.short_description = 'Image'


# =========================
# PROFILE ADMIN
# =========================
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'mobile_number', 'address')
    search_fields = ('user__username', 'mobile_number')
    list_per_page = 20


# =========================
# ORDER ITEM INLINE
# =========================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ('product_link', 'quantity', 'total_price_display')

    def product_link(self, obj):
        url = reverse('admin:shop_product_change', args=[obj.product.id])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = 'Product'

    def total_price_display(self, obj):
        return f"₹{obj.total_price()}"
    total_price_display.short_description = 'Item Total'


# =========================
# ORDER ADMIN
# =========================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status_colored', 'total_price_display', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__user__username',)
    ordering = ('-created_at',)
    list_per_page = 20
    inlines = [OrderItemInline]
    readonly_fields = ('total_price_display', 'created_at')

    fieldsets = (
        ('Order Info', {
            'fields': ('customer', 'status')
        }),
        ('Order Summary', {
            'fields': ('total_price_display', 'created_at')
        }),
    )

    def total_price_display(self, obj):
        return f"₹{obj.total_price()}"
    total_price_display.short_description = "Total Price"

    def status_colored(self, obj):
        color = {
            'Pending': 'orange',
            'Shipped': 'blue',
            'Delivered': 'green',
            'Cancelled': 'red'
        }.get(obj.status, 'black')
        return format_html('<b style="color:{};">{}</b>', color, obj.status)
    status_colored.short_description = 'Status'


# =========================
# WISHLIST & CART ADMIN
# =========================
@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'product__name')
    ordering = ('-created_at',)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ()


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'updated_at', 'total_items')
    search_fields = ('user__username',)
    ordering = ('-updated_at',)
    inlines = [CartItemInline]

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id','order','amount','status','razorpay_order_id','razorpay_payment_id','created_at')
    search_fields = ('razorpay_order_id','razorpay_payment_id','order__id')
    ordering = ('-created_at',)
