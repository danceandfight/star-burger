from django.db import models

class Place(models.Model):
    address = models.CharField('адрес', max_length=100, unique=True)
    lon = models.FloatField(verbose_name="Долгота", null=True)
    lat = models.FloatField(verbose_name="Широта", null=True)
    date = models.DateTimeField("Дата запроса к геокодеру")
