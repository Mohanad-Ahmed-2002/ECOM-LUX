# cart/context_processors.py
from django.db import models
from store.models import CartItem

def cart_item_count(request):
    session_key = request.session.session_key
    if not session_key:
        return {'cart_item_count': 0}

    total_quantity = CartItem.objects.filter(session_key=session_key).aggregate(total_quantity=models.Sum('quantity'))['total_quantity']
    
    return {
        'cart_item_count': total_quantity or 0
    }
