from django.urls import path
from . import views

urlpatterns = [
    # صفحات عامة
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),

    # المتجر
    path('shop/<str:main_category>/', views.products_by_main_category, name='products_by_main_category'),
    path('shop/<str:main_category>/<str:sub_category>/', views.products_by_main_and_sub_category, name='products_by_main_and_sub_category'),
    path('shop/<str:main_category>/<str:sub_category>/<str:age_group>/', views.products_by_main_sub_and_age, name='products_by_main_sub_and_age'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('hot-sale/', views.hot_sale_view, name='hot_sale'),

    # المفضلة
    path('favorite/', views.favoritelist, name='favorite'),
    path('add-to-wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

    # السلة
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/increase/<int:item_id>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:item_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # الطلب والدفع
    path('checkout/', views.checkout, name='checkout'),
    path('validate-promo/', views.validate_promo_code, name='validate_promo_code'),
    path('order_success/<int:order_id>/', views.order_success, name='order_success'),

    # لوحة التحكم
    path('dashboard/', views.dashboard_home, name='dashboard_home'),
    path('dashboard/orders/', views.dashboard_orders, name='dashboard_orders'),
    path('dashboard/orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('dashboard/orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('dashboard/orders/<int:order_id>/delete/', views.delete_order, name='delete_order'),
    path('dashboard/products/', views.dashboard_products, name='dashboard_products'),
    path('dashboard/products/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    
]
