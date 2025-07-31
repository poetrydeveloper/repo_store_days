from django.contrib import admin
from .models import Supplier


class BaseAdmin(admin.ModelAdmin):
    list_per_page = 50
    save_on_top = True

@admin.register(Supplier)
class SupplierAdmin(BaseAdmin):
    list_display = ('name', 'contact_person', 'phone', 'notes_short')
    search_fields = ('name', 'contact_person', 'phone')

    def notes_short(self, obj):
        return obj.notes[:50] + '...' if obj.notes else '-'
    notes_short.short_description = 'Примечания'