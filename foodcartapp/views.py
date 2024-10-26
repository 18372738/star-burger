import json
from django.http import JsonResponse
from django.templatetags.static import static
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
    orders_json = Order.objects.all()
    print(orders_json)
    try:
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
                    return Response({
                        'error': f"Продукт с id {product_id} не найден."
                    })

    except Exception as e:
        return Response({
            'error': str(e)
        })
    return Response({
        'message': 'Order created successfully',
        'order_id': order.id,
    })
