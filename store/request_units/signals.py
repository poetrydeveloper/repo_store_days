# requests/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps
from django.utils import timezone
from django.core.exceptions import ValidationError

# Получаем модели из правильных приложений
ProductUnit = apps.get_model('unit', 'ProductUnit')  # ← Из приложения unit
RequestItem = apps.get_model('request_units', 'RequestItem')  # ← Из request_units


@receiver(post_save, sender=RequestItem)
def create_product_units(sender, instance, created, **kwargs):
    if created and instance.is_customer_order:
        try:
            base_date = timezone.now().strftime("%Y%m%d%H%M")
            product_code = instance.product.code or 'SN'

            # Создаем ProductUnit для каждого заказанного товара
            for i in range(1, instance.quantity_ordered + 1):
                serial_number = f"{product_code}-{base_date}-{i:03d}"
                ProductUnit.objects.create(
                    product=instance.product,
                    request_item=instance,
                    serial_number=serial_number,
                    status='in_request'
                )
        except Exception as e:
            raise ValidationError(f"Ошибка создания ProductUnit: {str(e)}")