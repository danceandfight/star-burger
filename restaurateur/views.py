import requests
import datetime

from collections import defaultdict

from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.db.models import Q
from django.db.models import Prefetch

from foodcartapp.models import Product, Restaurant, FoodCart, RestaurantMenuItem, Entry
from places.models import Place

from geopy import distance
from operator import itemgetter


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


def get_menuitem_availability():
    restaurantsmenuitems = RestaurantMenuItem.objects.select_related(
        'restaurant',
        'product'
        )    
    menuitems_availability = defaultdict(list)
    for item in restaurantsmenuitems:
        menuitems_availability[item.product].append(item.restaurant)
    return menuitems_availability


def get_suitable_restaurant(menuitems, ordered_items):
    restaurants = [menuitems[item] for item in ordered_items]
    return set.intersection(*[set(restaurant) for restaurant in restaurants])


def get_or_create_place(api_key, place, saved_places):
    
    if place.address not in saved_places.keys():
        coordinates = fetch_coordinates(api_key, place.address)
        if not coordinates:
            lon = lat = None
        else:
            lon, lat = coordinates
        Place.objects.create(
            address=place.address,
            lon=lon,
            lat=lat,
            date=datetime.datetime.now()
        )
        return coordinates

    lon = saved_places[place.address]['lon']
    lat = saved_places[place.address]['lat']

    if not (lat or lon):
        return None
    return lon, lat
    

def fetch_coordinates(apikey, place):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    params = {"geocode": place, "apikey": apikey, "format": "json"}
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']
    
    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):

    orders = []
    orders_addresses = FoodCart.objects.values_list('address')
    restaurant_adresses = Restaurant.objects.values_list('address')
    saved_places = list(Place.objects.filter(
        Q(address__in=orders_addresses) | 
        Q(address__in=restaurant_adresses)).values())
    saved_places = {place['address']:place for place in saved_places}
    menuitems = get_menuitem_availability()
    unprocessed_orders = FoodCart.objects.filter(status='Unprocessed').get_original_price().prefetch_related(
        Prefetch('entries', 
        queryset=Entry.objects.select_related('product'))
        )
    for order in unprocessed_orders:
        place_coordinates = get_or_create_place(
            settings.YA_GEO_APIKEY,
            order, 
            saved_places
            )
        if place_coordinates:
            products = order.entries.all()
            ordered_products = [product.product for product in products]
            order_restraurants = get_suitable_restaurant(
                menuitems,
                ordered_products
                )
            
            restaurant_distances = []

            for restaurant in order_restraurants:
                restaurant_coordinates = get_or_create_place(
                    settings.YA_GEO_APIKEY,
                    restaurant,
                    saved_places
                    )
                distance_to_restaurant = distance.distance(
                    (restaurant_coordinates), 
                    (place_coordinates)
                    ).km
                restaurant_distances.append([restaurant.name, round(distance_to_restaurant, 1)])
            restaurant_distances = sorted(restaurant_distances, key=itemgetter(1))
        else:
            restaurant_distances = None

        order = {
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
            }
        orders.append(order)

    return render(
        request,
        template_name='order_items.html',
        context={
            'order_items': orders}
        )
