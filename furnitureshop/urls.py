from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as account_views

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),

    # Main shop app
    path('', include('shop.urls')),
    path('shop/', include('shop.urls')),

    # User accounts
    path('accounts/', include('accounts.urls')),

    # Custom Admin URLs
    path('admin-login/', account_views.admin_login_view, name='admin_login'),
    path('admin-register/', account_views.admin_register, name='admin_register'),
    path('admin-profile/', account_views.admin_profile, name='admin_profile'),
    path('admin-logout/', account_views.admin_logout_view, name='admin_logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)