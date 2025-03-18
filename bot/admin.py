from django.contrib import admin

from bot.models import Domain, TelegramUser


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    """Регистрация в админ панели модели Domain."""
    list_display = ['id', 'name', 'is_accessible', 'is_blocked_api', 'is_active', 'last_checked']


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    """Регистрация в админ панели модели TelegramUser."""
    list_display = ['id', 'chat_id']
