from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # -------------------
    # Home + Auth
    # -------------------
    path("", views.home, name="home"),
    path("search/", views.search_products, name="search_products"),
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # -------------------
    # Products
    # -------------------
    path("products/", views.all_products, name="all_products"),  # all products page
    path("categories/", views.categories, name="categories"),  # categories page
    path("products/category/<slug:category_slug>/", views.products_by_category, name="products_by_category"),  # filter by category
    path("products/<int:product_id>/", views.product_detail, name="product_detail"),  # product detail page
    path("buy/", views.buy_form, name="buy"),  # standalone order form
    path("billing/", views.billing_page, name="billing"),  # standalone billing page
    path("support/", views.support_page, name="support"),
    path("returns/", views.returns_page, name="returns"),
    path("track-order/", views.track_order_page, name="track_order"),
    path("offers/", views.offers_page, name="offers"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("order/success/<int:order_id>/", views.order_success, name="order_success"),
    path("order/pay/<int:order_id>/", views.pay_now, name="pay_now"),
    path("my-orders/", views.my_orders, name="my_orders"),
    path("order/cancel/<int:order_id>/", views.cancel_order, name="cancel_order"),
    path("order/invoice/<int:order_id>/", views.download_invoice, name="download_invoice"),
    path("payment/create/<int:order_id>/", views.payment_create, name="payment_create"),
    path("payment/verify/", views.payment_verify, name="payment_verify"),
    path("products/buy/<int:product_id>/", views.buy_now, name="buy_now"),  # legacy: redirect to buy
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("wishlist/toggle/<int:product_id>/", views.toggle_wishlist, name="toggle_wishlist"),
    path("wishlist-toggle/<int:product_id>/", views.wishlist_toggle, name="wishlist_toggle"),
    path("wishlist/", views.wishlist_page, name="wishlist_page"),
    path("cart/", views.cart_view, name="cart"),
    path("wishlist/", views.wishlist_view, name="wishlist"),
    # -------------------
    # Dashboard
    # -------------------
    path("dashboard/", views.dashboard, name="dashboard"),

    # -------------------
    # Profile
    # -------------------
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.edit_profile_view, name="edit_profile"),

    # -------------------
    # Password Reset (built-in views)
    # -------------------
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="shop/password_reset.html",
            email_template_name="shop/password_reset_email.txt",  # plain text part
            html_email_template_name="shop/password_reset_email.html",  # HTML part
            subject_template_name="shop/password_reset_subject.txt",
            success_url="/password-reset/done/"
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="shop/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="shop/password_reset_confirm.html",
            success_url="/reset/done/"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="shop/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
