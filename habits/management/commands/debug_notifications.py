from django.core.management.base import BaseCommand
import logging
from django.conf import settings
from django.contrib.auth import get_user_model
import requests

logger = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):
    help = 'Полная диагностика системы уведомлений'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Начинаем диагностику системы уведомлений...')

        # Шаг 1: Проверка настроек
        self.stdout.write('\n1. 🔧 Проверка настроек...')
        if not settings.TELEGRAM_BOT_TOKEN:
            self.stdout.write(self.style.ERROR('❌ TELEGRAM_BOT_TOKEN не настроен!'))
            return
        self.stdout.write(self.style.SUCCESS('✅ TELEGRAM_BOT_TOKEN настроен'))

        # Шаг 2: Проверка пользователей
        self.stdout.write('\n2. 👥 Проверка пользователей...')
        users_with_telegram = User.objects.filter(telegram_chat_id__isnull=False)
        self.stdout.write(f'Найдено пользователей с Telegram: {users_with_telegram.count()}')

        for user in users_with_telegram:
            self.stdout.write(
                f'   👤 {user.username}: chat_id={user.telegram_chat_id}, notifications={user.telegram_notifications}')

        if not users_with_telegram.exists():
            self.stdout.write(self.style.ERROR('❌ Нет пользователей с привязанным Telegram!'))
            return

        # Шаг 3: Проверка Telegram API
        self.stdout.write('\n3. 📡 Проверка Telegram API...')
        try:
            url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getMe"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                bot_info = response.json()
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Telegram API работает. Бот: {bot_info["result"]["username"]}'))
            else:
                self.stdout.write(self.style.ERROR(f'❌ Ошибка Telegram API: {response.status_code}'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Ошибка подключения к Telegram API: {e}'))
            return

        # Шаг 4: Пробная отправка сообщения
        self.stdout.write('\n4. 📨 Тестовая отправка сообщения...')
        user = users_with_telegram.first()

        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': user.telegram_chat_id,
            'text': '🧪 Тестовое сообщение из диагностики',
            'parse_mode': 'HTML'
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS('✅ Сообщение успешно отправлено!'))
                self.stdout.write('📱 Проверьте Telegram, должно прийти сообщение')
            else:
                self.stdout.write(self.style.ERROR(f'❌ Ошибка отправки: {response.status_code} - {response.text}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Ошибка: {e}'))

        self.stdout.write('\n🎯 Диагностика завершена!')