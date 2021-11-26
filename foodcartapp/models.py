from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import F, Sum, DecimalField
from django.core.exceptions import ValidationError
from django.utils import timezone

from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField('название', max_length=50)
    address = models.CharField('адрес', max_length=100, blank=True)
    contact_phone = models.CharField(
        'контактный телефон', 
        max_length=50, 
        blank=True
        )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


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
    category = models.ForeignKey(
        ProductCategory, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        verbose_name='категория',
        related_name='products'
        )
    price = models.DecimalField(
        'цена', 
        max_digits=8, 
        decimal_places=2, 
        validators=[MinValueValidator(0)]
        )
    image = models.ImageField('картинка')
    special_status = models.BooleanField(
        'спец.предложение', 
        default=False, 
        db_index=True
        )
    description = models.TextField('описание', max_length=200, blank=True)

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name="ресторан"
        )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт'
        )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
        )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class FoodCartQuerySet(models.QuerySet):
    def get_current_price(self):
        price = self.annotate(price=Sum(F('entries__product__price') * F('entries__quantity'), output_field=DecimalField()))
        return price

    def get_original_price(self):
        price = self.annotate(price=Sum(F('entries__price') * F('entries__quantity'), output_field=DecimalField()))
        return price


class FoodCart(models.Model):

    choices = (('Unprocessed', 'Не обработан'), ('Recieved', 'Доставлен'), ('In progress', 'В обработке'))
    payment_methods = (('Cash', 'Наличными'), ('By card', 'Картой'))

    firstname = models.CharField('Имя', max_length=20)
    lastname = models.CharField('Фамилия', max_length=30)
    address = models.CharField('адрес', max_length=100, blank=True)
    phonenumber = PhoneNumberField(
        'Нормализованный номер владельца', 
        max_length=20, 
        db_index=True
        )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='orders',
        blank=True,
        null=True,
        verbose_name="ресторан"
        )
    status = models.CharField(
        'Статус заказа',
        max_length=30,
        choices=choices,
        default=choices[0][0],
        db_index=True
        )
    payment_method = models.CharField(
        'Способ оплаты',
        max_length=30,
        choices=payment_methods,
        blank=True,
        db_index=True
        )
    comment = models.TextField('Комментарий', blank=True)
    registrated_at = models.DateTimeField(
        'Заказ зарегестрирован',
        blank=True,
        default=timezone.now,
        db_index=True
        )
    called_at = models.DateTimeField(
        'Звонок совершен',
        blank=True,
        null=True,
        db_index=True
        )
    delivered_at = models.DateTimeField(
        'Заказ доставлен',
        blank=True,
        null=True,
        db_index=True
        )
    
    objects = FoodCartQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'{self.address} {self.firstname} {self.lastname}'


class Entry(models.Model):
    product = models.ForeignKey(
        Product,
        related_name='entries',
        on_delete=models.CASCADE
        )
    order = models.ForeignKey(
        FoodCart,
        related_name='entries',
        on_delete=models.CASCADE
        )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0.0)],
        )

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'
