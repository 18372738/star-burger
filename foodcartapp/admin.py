from django.contrib import admin
from django.shortcuts import reverse
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.http import urlencode
from django.http import HttpResponseRedirect
from django.utils.http import url_has_allowed_host_and_scheme

from .models import Product
from .models import ProductCategory
from .models import Restaurant
from .models import RestaurantMenuItem
from .models import Order
from .models import OrderProduct
from star_burger import settings


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html('<img src="{url}" style="max-height: 200px;"/>', url=obj.image.url)
    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html('<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>', edit_url=edit_url, src=obj.image.url)
    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [
        OrderProductInline
    ]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            instance.user = request.user
            instance.save()
        formset.save_m2m()

    def response_change(self, request, obj):
        res = super(OrderAdmin, self).response_change(request, obj)
        next_url = request.GET.get('next')
        allowed_hosts = settings.ALLOWED_HOSTS
        require_https = False
        if  url_has_allowed_host_and_scheme(next_url, allowed_hosts, require_https):
            return HttpResponseRedirect(next_url)
        else:
            return res
