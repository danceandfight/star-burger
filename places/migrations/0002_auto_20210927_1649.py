# Generated by Django 3.0.7 on 2021-09-27 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='address',
            field=models.CharField(max_length=100, unique=True, verbose_name='адрес'),
        ),
    ]