# app/customers admin.py
from django.contrib import admin
from .models import Customer

class BaseAdmin(admin.ModelAdmin):
    """Базовый класс для админ-панели"""
    list_per_page = 50
    save_on_top = True


@admin.register(Customer)
class CustomerAdmin(BaseAdmin):
    list_display = ('name', 'phone', 'email', 'notes_short')
    search_fields = ('name', 'phone', 'email')

    def notes_short(self, obj):
        return obj.notes[:50] + '...' if obj.notes else '-'

    notes_short.short_description = 'Примечания'