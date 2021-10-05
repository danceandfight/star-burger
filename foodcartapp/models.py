from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import F, Sum, DecimalField
from django.core.exceptions import ValidationError
from django.utils import timezone

from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField('название', max_length=50)
    address = models.CharField('адрес', max_length=100, blank=True)
    contact_phone = models.CharField('контактный телефон', max_length=50, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'


class ProductQuerySet(models.QuerySet):
    def available(self):
        return self.distinct().filter(menu_items__availability=True)


class ProductCategory(models.Model):
    name = models.CharField('название', max_length=50)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField('название', max_length=50)
    category = models.ForeignKey(ProductCategory, null=True, blank=True, on_delete=models.SET_NULL,
                                 verbose_name='категория', related_name='products')
    price = models.DecimalField('цена', max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    image = models.ImageField('картинка')
    special_status = models.BooleanField('спец.предложение', default=False, db_index=True)
    description = models.TextField('описание', max_length=200, blank=True)

    objects = ProductQuerySet.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items',
                                   verbose_name="ресторан")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='menu_items',
                                verbose_name='продукт')
    availability = models.BooleanField('в продаже', default=True, db_index=True)

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]


class FoodCartQuerySet(models.QuerySet):
    def get_price(self):
        price = self.annotate(price=Sum(F('order_entries__product__price') * F('order_entries__quantity'), output_field=DecimalField()))
        return price


class FoodCart(models.Model):
    firstname = models.CharField('Имя', max_length=20)
    lastname = models.CharField('Фамилия', max_length=30)
    address = models.CharField('адрес', max_length=100, blank=True)
    phonenumber = PhoneNumberField("Нормализованный номер владельца", max_length=20, db_index=True)
    choices = (('Recieved', 'Доставлен'), ('In progress', 'В обработке'))
    payment_methods = (('Cash', 'Наличными'), ('By card', 'Картой'))
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='restaurant_orders',
        blank=True,
        null=True,
        verbose_name="ресторан")
    status = models.CharField(
        'Статус заказа',
        max_length=30,
        choices=choices,
        blank=True
        )
    payment_method = models.CharField(
        'Способ оплаты',
        max_length=30,
        choices=payment_methods,
        blank=True
        )
    comment = models.TextField('Комментарий', blank=True)
    registrated_at = models.DateTimeField(
        'Заказ зарегестрирован',
        blank=True,
        default=timezone.now
        )
    called_at = models.DateTimeField(
        'Звонок совершен',
        blank=True,
        null=True
        )
    delivered_at = models.DateTimeField(
        'Заказ доставлен',
        blank=True,
        null=True
        )
    objects = FoodCartQuerySet.as_manager()

    def __str__(self):
        return f'{self.address} {self.firstname} {self.lastname}'

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'


class Entry(models.Model):
    product = models.ForeignKey(Product, related_name='product_entries', null=True, on_delete=models.CASCADE)
    order = models.ForeignKey(FoodCart, related_name='order_entries', null=True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0.0)],
        null=True,
        blank=True
        )

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'
