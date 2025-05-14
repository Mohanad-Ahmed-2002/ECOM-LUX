import pytest
from store.models import Product,PromoCode
from django.utils import timezone
from datetime import datetime,timedelta
@pytest.fixture
def product():
    return Product.objects.create(
        name="Test Product",
        price=100,
        main_category="SUNGLASSES",
        image="https://via.placeholder.com/150",
        age_group="Men"
    )


@pytest.fixture
def promo_code():
    return PromoCode.objects.create(
        code="HONDA",
        discount_percentage=10,
        is_active=True,
        expiration_date=timezone.now() + timedelta(days=30)
    )
