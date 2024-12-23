# Generated by Django 5.1.2 on 2024-11-13 20:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0047_rename_paymennt_order_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='restaurant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='restaurants', to='foodcartapp.restaurant', verbose_name='ресторан'),
        ),
    ]