from django.db import models

class Place(models.Model):
    address = models.CharField('адрес', max_length=100, blank=True, unique=True)
    lon = models.FloatField(verbose_name="Долгота")
    lat = models.FloatField(verbose_name="Широта")
    date = models.DateTimeField("Дата запроса к геокодеру")

