import pytest
from store.services.cart_service  import get_or_create_session_key,add_product_to_cart
from store.models import CartItem
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware

def attach_session(request):
    """دالة بسيطة لتفعيل الجلسة على request"""
    middleware = SessionMiddleware(get_response=lambda r: None)
    middleware.process_request(request)
    request.session.save()

@pytest.mark.django_db
def test_get_or_create_session_key(client):
    session_key = get_or_create_session_key(client)
    assert isinstance(session_key,str)
    assert len(session_key)>0


@pytest.mark.django_db
def test_add_product_to_cart(product):

    factory=RequestFactory()

    request=factory.post('/',{'selected_color':'blue'})

    attach_session(request)  # ✅ هنا ربطنا الـ request بجلسة حقيقية


    add_product_to_cart(product.id,request)

    cart_items=CartItem.objects.all()

    assert cart_items.count()==1
    assert cart_items[0].product == product
    assert cart_items[0].quantity == 1
    assert cart_items[0].selected_color == 'blue'