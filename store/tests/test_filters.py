import pytest
from store.models import Product
from store.filters import filter_products


@pytest.mark.django_db
def test_filter_by_price_range():
    Product.objects.create(name="Cheap", price=50, main_category="SUNGLASSES", image="img1", age_group="Men")
    Product.objects.create(name="Expensive", price=300, main_category="SUNGLASSES", image="img2", age_group="Men")

    results = filter_products(price_filter="0-100")
    assert results.count() == 1
    assert results.first().name == "Cheap"


@pytest.mark.django_db
def test_sort_by_price_desc():
    Product.objects.create(name="Low", price=100, main_category="SUNGLASSES", image="img1", age_group="Men")
    Product.objects.create(name="High", price=300, main_category="SUNGLASSES", image="img2", age_group="Men")

    results = filter_products(sort_by="price_desc")
    names = [p.name for p in results]
    assert names == ["High", "Low"]


@pytest.mark.django_db
def test_filter_by_sub_category():
    Product.objects.create(name="Optical", price=100, main_category="OPTICAL", sub_category="OPTICAL", image="img", age_group="Men")
    Product.objects.create(name="Other", price=100, main_category="SUNGLASSES", sub_category="SUNGLASSES", image="img", age_group="Men")

    results = filter_products(category_filter="OPTICAL")
    assert results.count() == 1
    assert results.first().name == "Optical"
