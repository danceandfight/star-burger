import json

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view


from .models import Product
from .models import FoodCart, Entry


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            },
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    order_data = json.loads(request.body.decode())
    order = FoodCart.objects.create(
        customer_name=order_data['firstname'],
        customer_lastname=order_data['lastname'],
        customer_adress=order_data['address'],
        customer_phone=order_data['phonenumber']
        )
    for product in order_data['products']:
        Entry.objects.create(
            product=Product.objects.get(id=product['product']),
            order=order,
            quantity=product['quantity']
            )
    return JsonResponse({})

