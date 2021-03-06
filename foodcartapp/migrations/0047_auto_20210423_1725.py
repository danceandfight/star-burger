# Generated by Django 3.0.7 on 2021-04-23 14:25

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0046_foodcart_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='foodcart',
            name='called_at',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, verbose_name='Звонок совершен'),
        ),
        migrations.AddField(
            model_name='foodcart',
            name='delivered_at',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, verbose_name='Заказ доставлен'),
        ),
        migrations.AddField(
            model_name='foodcart',
            name='registrated_at',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, verbose_name='Заказ зарегестрирован'),
        ),
    ]
