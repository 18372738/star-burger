import json
import phonenumbers
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product, Order, OrderProduct


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
            } if product.category else None,
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
    try:
        required_fields = ['firstname', 'lastname', 'phonenumber', 'address', 'products']

        for field in required_fields:
            if not request.data.get(field):
                return Response(
                    {
                        'error': f'{field} - обязательное поле и не может быть пустым'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                    )

        phonenumber = request.data.get('phonenumber')
        parsed_number = phonenumbers.parse(phonenumber, "RU")
        if not phonenumbers.is_valid_number(parsed_number):
            return Response(
                {'error': 'Неверный формат телефона, должен быть для России.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(request.data['products'], list) or not request.data['products']:
            return Response(
                {
                    'error':  'products: Пустое значение или не список',
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        order = Order.objects.create(
            firstname=request.data['firstname'],
            lastname=request.data['lastname'],
            phonenumber=request.data['phonenumber'],
            address=request.data['address'],
        )

        for product in request.data['products']:
            try:
                product_id = product['product']
                quantity = product['quantity']
                product = Product.objects.get(id=product_id)
                OrderProduct.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity
                )
            except Product.DoesNotExist:
                return Response(
                    {
                        'error': f"Продукт с id {product_id} не найден."
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

    except KeyError as e:
        return Response(
            {'error': f'Нет данных: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {
                'error': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    return Response(
        {
            'message': 'Order created successfully',
            'order_id': order.id,
        },
        status=status.HTTP_201_CREATED
    )
