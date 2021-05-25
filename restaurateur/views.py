import requests

from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views

from foodcartapp.models import Product, Restaurant, FoodCart, RestaurantMenuItem
from places.models import Place

from geopy import distance
from environs import Env
from operator import itemgetter

env = Env()
env.read_env()


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

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:

        availability = {
            **default_availability,
            **{item.restaurant_id: item.availability for item in product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id] for restaurant in restaurants]

        products_with_restaurants.append(
            (product, orderer_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurants': products_with_restaurants,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


def get_burger_availability():
    restaurantsmenuitems = list(RestaurantMenuItem.objects.select_related('restaurant', 'product').all())
    burger_availability = {}
    for item in restaurantsmenuitems:
        if item.product.name not in burger_availability:
            burger_availability[item.product.name] = []
        if item.availability:
            burger_availability[item.product.name].append(item.restaurant.name)
    return burger_availability


def get_suitable_restaurant(menuitems, ordered_items):
    restaurant_list = []
    for item in ordered_items:
        if item in menuitems.keys():
            restaurant_list.append(menuitems[item])
    return set.intersection(*[set(list) for list in restaurant_list])


def fetch_coordinates(apikey, place):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    params = {"geocode": place, "apikey": apikey, "format": "json"}
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']
    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_restaurant_distance(order_address, restaurant_address):
    apikey = env('API_KEY')
    order_lon, order_lat = fetch_coordinates(apikey, order_address)
    address_lon, address_lat = fetch_coordinates(apikey, restaurant_address)
    distance_to_restaurant = distance.distance((order_lat, order_lon), (address_lat, address_lon)).km
    return round(distance_to_restaurant, 1)


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):

    orders_data = []
    menuitems = []
    restaurants = Restaurant.objects.all()

    if not menuitems:
        menuitems = get_burger_availability()

    for order in FoodCart.objects.get_price():
        products = order.order_entries.all()
        ordered_products_list = [product.product.name for product in products]
        order_restraurants = get_suitable_restaurant(menuitems, ordered_products_list)
        order_address = order.address

        restaurant_distances = []

        for restaurant in order_restraurants:
            restaurant = restaurants.get(name=restaurant)
            restaurant_address = restaurant.address
            restaurant_name = restaurant.name
            distance = get_restaurant_distance(order_address, restaurant_address)
            restaurant_distances.append([restaurant_name, distance])
        #sorted_restaurant_distances = []
        #for restaurant in sorted(restaurant_distances, key=itemgetter(1)):
            #sorted_restaurant_distances.append(f'{restaurant[0]} - {restaurant[1]} км')
        restaurant_distances = sorted(restaurant_distances, key=itemgetter(1))

        order_data = {
            'id': order.id,
            'price': order.price,
            'firstname': order.firstname,
            'lastname': order.lastname,
            'phonenumber': order.phonenumber,
            'address': order.address,
            'status': order.get_status_display(),
            'comment': order.comment,
            'payment_method': order.get_payment_method_display(),
            'restaurant': restaurant_distances
            #'restaurant': sorted_restaurant_distances
            }
        orders_data.append(order_data)

    return render(
        request,
        template_name='order_items.html',
        context={
            'order_items': orders_data}
        )

"""
@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):

    orders_data = []
    menuitems = []
    restaurants = Restaurant.objects.all()

    if not menuitems:
        menuitems = get_burger_availability()

    for order in FoodCart.objects.get_price():
        products = order.order_entries.all()
        ordered_products_list = [product.product.name for product in products]
        order_restraurants = get_suitable_restaurant(menuitems, ordered_products_list)

        restaurant_distances = []

        for restaurant in order_restraurants:
            restaurant = restaurants.get(name=restaurant)
            restaurant_address = restaurant.address
            restaurant_name = restaurant.name
            distance = get_restaurant_distance(order.address, restaurant_address)
            restaurant_distances.append([restaurant_name, distance])
        sorted_restaurant_distances = []
        for restaurant in sorted(restaurant_distances, key=itemgetter(1)):
            sorted_restaurant_distances.append(f'{restaurant[0]} - {restaurant[1]} км')

        order_data = {
            'id': order.id,
            'price': order.price,
            'firstname': order.firstname,
            'lastname': order.lastname,
            'phonenumber': order.phonenumber,
            'address': order.address,
            'status': order.get_status_display(),
            'comment': order.comment,
            'payment_method': order.get_payment_method_display(),
            'restaurant': sorted_restaurant_distances
            }
        orders_data.append(order_data)

    return render(
        request,
        template_name='order_items.html',
        context={
            'order_items': orders_data}
        )

"""