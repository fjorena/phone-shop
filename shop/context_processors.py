from .models import Cart


def cart_count(request):
    if request.user.is_authenticated:
        try:
            return {'cart_count': request.user.cart.total_items}
        except Cart.DoesNotExist:
            pass
    return {'cart_count': 0}
