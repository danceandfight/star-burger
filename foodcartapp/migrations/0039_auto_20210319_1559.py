# Generated by Django 3.0.7 on 2021-03-19 12:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0038_entry_foodcart'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='foodcart',
            options={'verbose_name': 'заказ', 'verbose_name_plural': 'заказы'},
        ),
    ]
