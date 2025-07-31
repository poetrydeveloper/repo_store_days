# unit  models.py
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.crypto import get_random_string


class ProductUnit(models.Model):
    """Виртуальная карта единицы товара"""

    STATUS_CHOICES = [
        ('created', 'Создан'),
        ('in_request', 'В заявке'),
        ('in_supply', 'Поставка'),
        ('in_store', 'В магазине'),
        ('sold', 'Продано'),
        ('returned', 'Возврат'),
        ('lost', 'Утерян'),
        ('transfer', 'Перемещение'),
    ]

    serial_number = models.CharField(
        'Серийный номер',
        max_length=100,
        unique=True,
        blank=True  # Разрешаем временно пустое значение для генерации
    )

    product = models.ForeignKey(
        'product.Product',
        on_delete=models.PROTECT,
        verbose_name='Товар'
    )

    request_item = models.ForeignKey(
        'request_units.RequestItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Позиция заявки'
    )

    supply_item = models.ForeignKey(
        'deliveries.SupplyItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Позиция поставки'
    )

    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default='created'
    )

    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        'Дата обновления',
        auto_now=True
    )

    class Meta:
        verbose_name = 'Единица товара'
        verbose_name_plural = 'Единицы товаров'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} - {self.serial_number} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        """Генерация серийного номера при создании"""
        if not self.serial_number:
            self.serial_number = self.generate_serial_number()
        super().save(*args, **kwargs)

    def generate_serial_number(self):
        """Улучшенная генерация серийного номера"""
        prefix = (self.product.sku[:3] if self.product and self.product.sku else 'SN').upper()
        max_attempts = 10
        attempt = 0

        while attempt < max_attempts:
            random_part = get_random_string(8, allowed_chars='0123456789ABCDEF')
            new_serial = f"{prefix}-{random_part}"
            if not ProductUnit.objects.filter(serial_number=new_serial).exists():
                return new_serial
            attempt += 1

        raise ValueError('Не удалось сгенерировать уникальный серийный номер')

    def clean(self):
        """Валидация перед сохранением"""
        if not self.serial_number:
            raise ValidationError({'serial_number': 'Серийный номер обязателен'})
        if len(self.serial_number) > 100:
            raise ValidationError({'serial_number': 'Максимальная длина 100 символов'})

    class Meta:
        indexes = [
            models.Index(fields=['serial_number']),
            models.Index(fields=['status']),
            models.Index(fields=['product', 'status']),
        ]