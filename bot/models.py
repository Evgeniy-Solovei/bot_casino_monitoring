from django.db import models


class Domain(models.Model):
    """Доменное имя"""
    name = models.CharField(max_length=50, unique=True, verbose_name='Доменное имя')
    is_accessible = models.BooleanField(default=True, verbose_name='Доступность домена (HTTP 200)')
    is_blocked_api = models.BooleanField(default=False, verbose_name='Блокировка домена API')
    is_active = models.BooleanField(default=True, verbose_name='Активный домен для проверки')
    last_checked = models.DateTimeField(auto_now=True, verbose_name='Последняя проверка')
    pay_domains = models.BooleanField(default=False, verbose_name='Куплен домен на замену')

    def __str__(self):
        return self.name


class TelegramUser(models.Model):
    """Хранит chat_id пользователей, отправивших команду /start боту"""
    chat_id = models.BigIntegerField(unique=True, verbose_name='Telegram Chat ID')

    def __str__(self):
        return str(self.chat_id)
