from store.models import CartItem, Product
from django.shortcuts import get_object_or_404
from decimal import Decimal


def get_or_create_session_key(request):
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    return session_key

def add_product_to_cart(product_id, request):
    session_key = get_or_create_session_key(request)
    product = Product.objects.get(id=product_id)
    selected_color = request.POST.get('selected_color')  # خد اللون اللي اختاره الزبون

    cart_item, created = CartItem.objects.get_or_create(
        session_key=session_key,
        product=product,
        defaults={'quantity': 1, 'selected_color': selected_color}
    )

    if not created:
        cart_item.quantity += 1
        if selected_color:
            cart_item.selected_color = selected_color
        cart_item.save()

    return product

def increase_cart_item_quantity(item_id, request):
    session_key = get_or_create_session_key(request)
    cart_item = get_object_or_404(CartItem, id=item_id, session_key=session_key)
    cart_item.quantity += 1
    cart_item.save()

def decrease_cart_item_quantity(item_id, request):

    session_key = get_or_create_session_key(request)
    cart_item = get_object_or_404(CartItem, id=item_id, session_key=session_key)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

def get_cart_items_and_total(session_key):
    cart_items = CartItem.objects.filter(session_key=session_key)
    total_price = sum(Decimal(item.get_total_price()) for item in cart_items)
    return cart_items, total_price

