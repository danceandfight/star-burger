# Generated by Django 3.0.7 on 2021-03-25 12:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0039_auto_20210319_1559'),
    ]

    operations = [
        migrations.RenameField(
            model_name='foodcart',
            old_name='customer_adress',
            new_name='address',
        ),
        migrations.RenameField(
            model_name='foodcart',
            old_name='customer_name',
            new_name='firstname',
        ),
        migrations.RenameField(
            model_name='foodcart',
            old_name='customer_lastname',
            new_name='lastname',
        ),
        migrations.RenameField(
            model_name='foodcart',
            old_name='customer_phone',
            new_name='phonenumber',
        ),
    ]
