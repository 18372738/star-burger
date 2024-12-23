from django.db import models
from django.utils import timezone


class Place(models.Model):
    address = models.CharField('Адрес', max_length=100)
    lat = models.FloatField('Широта')
    lon = models.FloatField('Долгота')
    geocode_date = models.DateField('Дата запроса', default=timezone.now,)

    def __str__(self):
        return self.address
