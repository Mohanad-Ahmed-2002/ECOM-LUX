import pytest
from store.models import CartItem
from store.services.order_service import calculate_total_prices,apply_promo_code


@pytest.mark.django_db
def test_calculate_total_prices(product):

    session_key= "test-session-312002"

    CartItem.objects.create(product=product,session_key=session_key,quantity=2)

    result=calculate_total_prices(session_key)

    assert result['subtotal'] == product.price*2
    assert result['shipping_fee'] == 70
    assert result ['total'] == result['subtotal'] + result['shipping_fee']


@pytest.mark.django_db
def test_apply_promo_code(promo_code):

    subtotal= 500
    discount = apply_promo_code('HONDA',subtotal)
    expected_discount = (subtotal * promo_code.discount_percentage) / 100

    assert discount == expected_discount

@pytest.mark.django_db
def test_apply_invalid_promo_code():

    subtotal = 500
    discount=apply_promo_code("JEANSCLUB",subtotal)

    assert discount == 0

