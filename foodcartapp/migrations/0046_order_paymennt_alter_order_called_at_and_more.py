# Generated by Django 5.1.2 on 2024-11-13 20:15

import django.utils.timezone
import phonenumber_field.modelfields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0045_order_called_at_order_delivered_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='paymennt',
            field=models.CharField(choices=[('not specified', 'Не указано'), ('cash', 'Наличный расчет'), ('non-cash', 'Безналичный расчет')], db_index=True, default='not specified', max_length=30, verbose_name='Способ оплаты'),
        ),
        migrations.AlterField(
            model_name='order',
            name='called_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='Дата звонка'),
        ),
        migrations.AlterField(
            model_name='order',
            name='delivered_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='Дата доставки'),
        ),
        migrations.AlterField(
            model_name='order',
            name='phonenumber',
            field=phonenumber_field.modelfields.PhoneNumberField(db_index=True, max_length=128, region=None, verbose_name='телефон'),
        ),
        migrations.AlterField(
            model_name='order',
            name='registrated_at',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='Дата создания'),
        ),
    ]