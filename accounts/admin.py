from django.contrib import admin
from .models import AdminProfile

@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'shop_name', 'admin_role')
    search_fields = ('user__username', 'phone', 'shop_name')
    list_filter = ('admin_role',)
    list_per_page = 20
    
    fieldsets = (
        ('User Info', {
            'fields': ('user',)
        }),
        ('Contact Details', {
            'fields': ('phone', 'shop_name', 'address')
        }),
        ('Admin Details', {
            'fields': ('admin_role', 'security_question')
        }),
    )