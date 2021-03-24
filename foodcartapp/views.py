import json

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

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
    order_data = request.data
    error = {}
    if 'products' not in order_data or \
        not isinstance(order_data['products'], list) or \
        not order_data['products']:
        error = {'error': 'Products key is not presented or not list'}
    elif 'firstname' not in order_data or \
        not order_data['firstname'] or \
        order_data['firstname'] == []:
        error = {'error': 'the key "firstname" is not specified or not str'}
    elif 'lastname' not in order_data or \
        not order_data['lastname']:
        error = {'error': 'the key "lastname" is not specified or not presented'}
    elif 'phonenumber' not in order_data or \
        not order_data['phonenumber'] or \
        order_data['phonenumber'] == '':
        error = {'error': 'the key "phonenumber" is not specified or not presented'}
    elif 'address' not in order_data or \
        not order_data['address']:
        error = {'error': 'the key "address" is not specified or not presented'}
    else:
        for product in order_data['products']:
            if not isinstance(product['product'], int):
                error = {'error': 'Product key is not presented or not list'}
                return Response(error, status=status.HTTP_404_NOT_FOUND)
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
    return Response(error)
