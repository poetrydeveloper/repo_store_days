from django.db import models

class CashDay(models.Model):
    date = models.DateField(verbose_name="Дата", unique=True)
    cash_sales_total = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=0, verbose_name="Общая сумма наличных продаж"
    )
    cash_sales_count = models.PositiveIntegerField(
        default=0, verbose_name="Количество наличных продаж"
    )
    card_sales_total = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=0, verbose_name="Общая сумма продаж картой"
    )
    card_sales_count = models.PositiveIntegerField(
        default=0, verbose_name="Количество продаж картой"
    )
    total_sales = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=0, verbose_name="Итоговая выручка за день"
    )
    is_closed = models.BooleanField(
        default=False, verbose_name="День закрыт"
    )

    def __str__(self):
        return f"Торговый день: {self.date.strftime('%d.%m.%Y')}"

    def update_totals(self):
        """Обновление итоговых значений при закрытии дня"""
        self.total_sales = self.cash_sales_total + self.card_sales_total
        self.save()

    class Meta:
        verbose_name = "Торговый день"
        verbose_name_plural = "Торговые дни"


class SaleEvent(models.Model):
    EVENT_TYPES = [
        ('sale', 'Продажа'),
        ('price_request', 'Запрос цены'),
        ('order', 'Заказ'),
        ('custom_order_sale', 'Продажа заказного товара'),
        ('return', 'Возврат товара'),
        ('fitting', 'Примерка товара'),
    ]
    PAYMENT_TYPES = [
        ('cash', 'Наличные'),
        ('card', 'Карта'),
        ('none', 'Без оплаты'),  # Для событий без платежа
    ]

    cash_day = models.ForeignKey(
        CashDay, on_delete=models.CASCADE,
        verbose_name="Торговый день"
    )
    event_type = models.CharField(
        max_length=20, choices=EVENT_TYPES,
        verbose_name="Тип события"
    )
    payment_type = models.CharField(
        max_length=10, choices=PAYMENT_TYPES,
        default='none', verbose_name="Тип оплаты"
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0, verbose_name="Сумма"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True, verbose_name="Время события"
    )
    notes = models.TextField(
        blank=True, null=True, verbose_name="Комментарий"
    )

    def save(self, *args, **kwargs):
        """Автоматическое обновление статистики дня при сохранении"""
        super().save(*args, **kwargs)

        if self.event_type == 'sale' and self.payment_type in ['cash', 'card']:
            cash_day = self.cash_day
            if self.payment_type == 'cash':
                cash_day.cash_sales_total += self.amount
                cash_day.cash_sales_count += 1
            elif self.payment_type == 'card':
                cash_day.card_sales_total += self.amount
                cash_day.card_sales_count += 1

            cash_day.update_totals()

    def __str__(self):
        return f"{self.get_event_type_display()} - {self.amount} руб."