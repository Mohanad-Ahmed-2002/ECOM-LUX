from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about', views.about, name='about'),
    path('shop/<str:main_category>/', views.products_by_main_category, name='products_by_main_category'),
    path('shop/<str:main_category>/<str:sub_category>/', views.products_by_main_and_sub_category, name='products_by_main_and_sub_category'),
    path('shop/<str:main_category>/<str:sub_category>/<str:age_group>/', views.products_by_main_sub_and_age, name='products_by_main_sub_and_age'),
    path('favorite', views.favoritelist, name='favorite'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/increase/<int:item_id>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:item_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('checkout/',views.checkout,name='checkout'),
    path('payment-redirect/', views.payment_redirect, name='payment_redirect'),
    path('validate-promo/', views.validate_promo_code, name='validate_promo_code'),
    path('order_success/<int:order_id>/', views.order_success, name='order_success'),
    path('add-to-wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('add-to-wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('dashboard/orders/', views.dashboard_orders, name='dashboard_orders'),
    path('dashboard/orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('dashboard/orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('dashboard/orders/<int:order_id>/delete/', views.delete_order, name='delete_order'),


]

