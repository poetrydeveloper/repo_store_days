# app/customers models.py
from django.db import models

class Customer(models.Model):
    """Клиент (покупатель)"""
    name = models.CharField('Наименование', max_length=255)
    phone = models.CharField('Телефон', max_length=20)
    email = models.EmailField('Email', blank=True)
    notes = models.TextField('Примечания', blank=True)

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['name']

    def __str__(self):
        return self.name