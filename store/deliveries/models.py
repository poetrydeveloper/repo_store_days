from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from store.suppliers.models import Supplier


class Delivery(models.Model):
    """Поставка (заголовок)"""
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        verbose_name='Поставщик'
    )
    delivery_date = models.DateField('Дата поставки')
    total_amount = models.DecimalField(
        'Сумма поставки',
        max_digits=12,
        decimal_places=2,
        default=0
    )
    notes = models.TextField('Примечания', blank=True)

    class Meta:
        verbose_name = 'Поставка'
        verbose_name_plural = 'Поставки'
        ordering = ['-delivery_date']

    def __str__(self):
        return f"Поставка #{self.id} от {self.delivery_date}"


.class DeliveryItem(models.Model):
    delivery = models.ForeignKey(   # нету
        'unit.Delivery',
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Поставка'
    )
    product = models.ForeignKey(
        'goods.Product',
        on_delete=models.PROTECT,
        verbose_name='Товар'
    )
    quantity_received = models.PositiveIntegerField(
        'Количество получено',
        validators=[MinValueValidator(1)],
        default=1
    )
    price_per_unit = models.DecimalField(
        'Цена за единицу',
        max_digits=10,
        decimal_places=2
    )
    request_item = models.ForeignKey(
        'warehouse.RequestItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='delivery_items',
        verbose_name='Связанная заявка'
    )
    received_units = models.ManyToManyField(
        'unit.ProductUnit',
        related_name='delivery_items_received',
        verbose_name='Полученные единицы',
        blank=True
    )

    class Meta:
        verbose_name = 'Позиция поставки'
        verbose_name_plural = 'Позиции поставок'
        ordering = ['delivery', 'product']

    def __str__(self):
        return f"{self.product.name} x {self.quantity_received} (Поставка #{self.delivery.id})"

    def clean(self):
        """Валидация данных перед сохранением"""
        errors = {}

        if self.quantity_received is None:
            errors['quantity_received'] = 'Укажите количество'
        elif self.quantity_received <= 0:
            errors['quantity_received'] = 'Количество должно быть положительным'

        if self.price_per_unit is None:
            errors['price_per_unit'] = 'Укажите цену'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """
        Сохранение с обработкой полученных единиц
        """
        # Временное хранение units перед сохранением
        tmp_units = list(self.received_units.all()) if self.pk else []

        # Основное сохранение
        super().save(*args, **kwargs)

        # Обновление статусов units
        if tmp_units:
            from django.db.models import F
            self.received_units.set(tmp_units)
            self.received_units.filter(status__in=['in_request', 'in_store']).update(
                status='in_store'
            )

    @property
    def total_price(self):
        """Вычисляемая общая сумма"""
        if self.quantity_received and self.price_per_unit:
            return self.quantity_received * self.price_per_unit
        return None

    def get_received_units_info(self):
        """Информация о полученных единицах"""
        return [
            {
                'id': unit.id,
                'serial_number': unit.serial_number,
                'status': unit.status
            }
            for unit in self.received_units.all()
        ]
