from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction

from rest_framework.serializers import ModelSerializer

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


class EntrySerializer(ModelSerializer):
    class Meta:
        model = Entry
        fields = ['product', 'quantity']


class FoodCartSerializer(ModelSerializer):
    products = EntrySerializer(many=True, write_only=True, allow_empty=False)

    class Meta:
        model = FoodCart
        fields = ['id', 'firstname', 'lastname', 'phonenumber', 'address', 'products']

@transaction.atomic
@api_view(['POST'])
def register_order(request):
    serializer = FoodCartSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    order = FoodCart.objects.create(
        firstname=serializer.validated_data['firstname'],
        lastname=serializer.validated_data['lastname'],
        address=serializer.validated_data['address'],
        phonenumber=serializer.validated_data['phonenumber']
        )
    entries = serializer.validated_data['products']
    for entry in entries:
        Entry.objects.create(
            order=order,
            product=entry['product'],
            quantity=entry['quantity'],
            price=entry['product'].price
            )
    frontend_serialized_order = FoodCartSerializer(order)
    return Response(frontend_serialized_order.data)
