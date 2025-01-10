import requests
from geopy import distance

from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Prefetch, Sum

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views

from star_burger import settings
from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem
from place.models import Place


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


def get_available_restaurants(orders):
    menu_items = RestaurantMenuItem.objects.filter(availability=True).select_related('product', 'restaurant')
    restaurant_products = {}
    for item in menu_items:
        if item.restaurant not in restaurant_products:
            restaurant_products[item.restaurant] = set()
        restaurant_products[item.restaurant].add(item.product)

    for order in orders:
        products = set(order.products.all())
        available_restaurants = []
        for restaurant, products_in_menu in restaurant_products.items():
            if products.issubset(products_in_menu):
                available_restaurants.append(restaurant)
        order.available_restaurants = available_restaurants

    return orders


def get_coordinates(orders):
    client_addresses = set()
    restaurant_addresses = set()
    for order in orders:
        client_addresses.add(order.address)
        for restaurant in order.available_restaurants:
            restaurant_addresses.add(restaurant.address)
    all_addresses = client_addresses | restaurant_addresses
    places = Place.objects.filter(address__in=all_addresses)
    coordinates = {place.address: (place.lon, place.lat) for place in places}
    addresses = set(all_addresses) - set(coordinates.keys())

    for address in addresses:
        fetched_coordinates = fetch_coordinates(settings.YANDEX_API_KEY, address)
        if fetched_coordinates:
            Place.objects.get_or_create(
                address=address,
                lat=fetched_coordinates[1],
                lon=fetched_coordinates[0],
            )
            coordinates[address] = fetched_coordinates
        else:
            Place.objects.get_or_create(
                address=address
            )

    return coordinates


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = (
        Order.objects.exclude(status='delivered')
        .prefetch_related('products')
        .annotate(total_cost=Sum('products__price'))
        .order_by('status')
    )
    orders = get_available_restaurants(orders)
    coordinates = get_coordinates(orders)

    for order in orders:
        restaurants_with_distance = []
        for restaurant in order.available_restaurants:
            restaurant_coords = coordinates.get(restaurant.address)
            client_coords = coordinates.get(order.address)

            if client_coords and restaurant_coords:
                geopy_distance = round(distance.distance(client_coords[::-1], restaurant_coords[::-1]).km, 2)
            else:
                geopy_distance = 'Ошибка определения координат'

            restaurants_with_distance.append({
                'restaurant': restaurant,
                'distance': geopy_distance,
            })

        order.restaurants = restaurants_with_distance

    return render(request, 'order_items.html', {'order_items': orders})
