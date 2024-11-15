# Generated by Django 5.1.2 on 2024-11-15 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0049_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('0', 'Необработанный'), ('1', 'На сборке'), ('2', 'Передан курьеру'), ('3', 'Доставлен')], db_index=True, default='0', max_length=30, verbose_name='Статус'),
        ),
    ]
