from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import Sum, F, Count
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone


ORDER_STATUS = (
    ('unprocessed', 'Необработанный'),
    ('order_assembly', 'На сборке'),
    ('delivering', 'Передан курьеру'),
    ('delivered', 'Доставлен'),
)


PAYMENT_CHOICES = (
    ('not specified', 'Не указано'),
    ('cash', 'Наличный расчет'),
    ('non-cash', 'Безналичный расчет'),
)


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=400,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def total_cost(self):
        return self.annotate(
            total_cost=Sum(F('orders__price') * F('orders__quantity'))
        )


class Order(models.Model):
    status = models.CharField(
        verbose_name='Статус',
        choices=ORDER_STATUS,
        max_length=30,
        default='unprocessed',
        db_index=True
    )
    payment = models.CharField(
        verbose_name='Способ оплаты',
        choices=PAYMENT_CHOICES,
        max_length=30,
        default='not specified',
        db_index=True
    )
    firstname = models.CharField(
        'имя',
        max_length=30
    )
    lastname = models.CharField(
        'фамилия',
        max_length=50
    )
    phonenumber = PhoneNumberField('телефон', db_index=True)
    address = models.CharField(
        'адрес',
        max_length=100,
    )
    restaurant = models.ForeignKey(
        Restaurant,
        verbose_name='ресторан',
        related_name='restaurants',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    comment = models.TextField(
        'комментарий',
        max_length=300,
        blank=True
    )
    products = models.ManyToManyField(
        Product,
        through='OrderProduct'
    )
    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        default=timezone.now,
        db_index=True,
    )
    called_at = models.DateTimeField(
        verbose_name='Дата звонка',
        blank=True,
        null=True,
        db_index=True,
    )
    delivered_at = models.DateTimeField(
        verbose_name='Дата доставки',
        blank=True,
        null=True,
        db_index=True,
    )
    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f"{self.id} - {self.address}"


class OrderProduct(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='заказ',
    )
    product = models.ForeignKey(
        Product,
        related_name='order_products',
        verbose_name='продукт',
        on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(
        verbose_name='количество',
        default=1,
        validators=[MinValueValidator(1)],
    )
    price = models.DecimalField(
        'стоимость',
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return f'{self.order} - {self.product.name} ({self.quantity})'
