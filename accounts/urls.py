from django.urls import path
from . import views

urlpatterns = [
    # Custom Admin Authentication URLs
    path('register/', views.admin_register, name='admin_register'),
    path('login/', views.admin_login_view, name='admin_login'),
    path('profile/', views.admin_profile, name='admin_profile'),
    path('logout/', views.admin_logout_view, name='admin_logout'),

    # Extra route for admin edit profile (avoid name clash with shop's user edit)
    path('edit-profile/', views.edit_profile, name='admin_edit_profile'),
]
