from django.contrib import admin
from .models import CashDay, SaleEvent


@admin.register(CashDay)
class CashDayAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_sales', 'cash_sales_total', 'card_sales_total', 'is_closed')
    list_filter = ('date', 'is_closed')
    search_fields = ('date',)
    date_hierarchy = 'date'
    ordering = ('-date',)

    fieldsets = (
        ('Основная информация', {
            'fields': ('date', 'is_closed')
        }),
        ('Наличные расчеты', {
            'fields': ('cash_sales_total', 'cash_sales_count')
        }),
        ('Безналичные расчеты', {
            'fields': ('card_sales_total', 'card_sales_count')
        }),
        ('Итоги', {
            'fields': ('total_sales',)
        }),
    )

    readonly_fields = ('total_sales',)


@admin.register(SaleEvent)
class SaleEventAdmin(admin.ModelAdmin):
    list_display = ('cash_day', 'event_type_display', 'payment_type_display', 'amount', 'timestamp')
    list_filter = ('event_type', 'payment_type', 'cash_day')
    search_fields = ('cash_day__date', 'notes')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)

    fieldsets = (
        ('Основная информация', {
            'fields': ('cash_day', 'event_type', 'payment_type', 'amount')
        }),
        ('Дополнительно', {
            'fields': ('notes', 'timestamp')
        }),
    )

    readonly_fields = ('timestamp',)

    def event_type_display(self, obj):
        return obj.get_event_type_display()

    event_type_display.short_description = 'Тип события'

    def payment_type_display(self, obj):
        return obj.get_payment_type_display()

    payment_type_display.short_description = 'Тип оплаты'