# Generated by Django 3.0.7 on 2021-05-24 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(blank=True, max_length=100, unique=True, verbose_name='адрес')),
                ('lon', models.FloatField(verbose_name='Долгота')),
                ('lat', models.FloatField(verbose_name='Широта')),
                ('date', models.DateTimeField(verbose_name='Дата запроса к геокодеру')),
            ],
        ),
    ]
