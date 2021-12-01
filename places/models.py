from django.db import models

class Place(models.Model):
    address = models.CharField('адрес', max_length=100, unique=True)
    lon = models.FloatField(verbose_name="Долгота", blank=True, null=True)
    lat = models.FloatField(verbose_name="Широта", blank=True, null=True)
    date = models.DateTimeField("Дата запроса к геокодеру")
