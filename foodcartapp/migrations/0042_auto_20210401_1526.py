# Generated by Django 3.0.7 on 2021-04-01 12:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0041_auto_20210326_1916'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_entries', to='foodcartapp.FoodCart'),
        ),
        migrations.AlterField(
            model_name='entry',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_entries', to='foodcartapp.Product'),
        ),
    ]
