from django.db import models
from django.utils import timezone


class Place(models.Model):
    address = models.CharField('Адрес', max_length=100)
    lat = models.FloatField('Широта', null=True, blank=True)
    lon = models.FloatField('Долгота', null=True, blank=True)
    geocode_date = models.DateField('Дата запроса', default=timezone.now,)

    def __str__(self):
        return self.address
