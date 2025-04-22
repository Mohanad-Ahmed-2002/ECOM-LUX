from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about', views.about, name='about'),
    path('favorite', views.favoritelist, name='favorite'),
    path('man', views.men_products, name='men_products'),
    path('woman', views.women_products, name='women_products'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/increase/<int:item_id>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:item_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('checkout/',views.checkout,name='checkout'),
    path('order_success/<int:order_id>/', views.order_success, name='order_success'),
]

