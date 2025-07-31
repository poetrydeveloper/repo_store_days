# unit  admin
from django.contrib import admin
from django.utils.html import format_html
from .models import ProductUnit

@admin.register(ProductUnit)
class ProductUnitAdmin(admin.ModelAdmin):
    list_display = (
        'serial_number',
        'product_link',
        'status_display',
        'request_item_link',
        'supply_item_link',
        'created_at',
        'updated_at',
    )
    list_filter = (
        'status',
        'created_at',
        'product',
    )
    search_fields = (
        'serial_number',
        'product__name',
        'product__sku',
        'request_item__id',
        'supply_item__id',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
        'serial_number',
    )
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'product',
                'serial_number',
                'status',
            )
        }),
        ('Связанные объекты', {
            'fields': (
                'request_item',
                'supply_item',
            )
        }),
        ('Даты', {
            'fields': (
                'created_at',
                'updated_at',
            )
        }),
    )
    list_select_related = (
        'product',
        'request_item',
        'supply_item',
    )
    list_per_page = 50
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    def product_link(self, obj):
        if obj.product:
            url = f"/admin/product/product/{obj.product.id}/change/"
            return format_html('<a href="{}">{}</a>', url, obj.product.name)
        return "-"
    product_link.short_description = 'Товар'
    product_link.admin_order_field = 'product__name'

    def status_display(self, obj):
        return obj.get_status_display()
    status_display.short_description = 'Статус'
    status_display.admin_order_field = 'status'

    def request_item_link(self, obj):
        if obj.request_item:
            url = f"/admin/warehouse/requestitem/{obj.request_item.id}/change/"
            return format_html('<a href="{}">Заявка #{}</a>', url, obj.request_item.id)
        return "-"
    request_item_link.short_description = 'Позиция заявки'

    def supply_item_link(self, obj):
        if obj.supply_item:
            url = f"/admin/deliveries/supplyitem/{obj.supply_item.id}/change/"
            return format_html('<a href="{}">Поставка #{}</a>', url, obj.supply_item.id)
        return "-"
    supply_item_link.short_description = 'Позиция поставки'

    def get_readonly_fields(self, request, obj=None):
        """Делаем serial_number изменяемым только при создании"""
        if obj:  # Редактирование существующего объекта
            return self.readonly_fields + ('serial_number',)
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        """Дополнительная валидация при сохранении из админки"""
        obj.clean()
        super().save_model(request, obj, form, change)