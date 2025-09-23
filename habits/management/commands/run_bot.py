from django.core.management.base import BaseCommand
from habits.telegram_bot import HabitTrackerBot
import logging
import asyncio

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Запуск Telegram бота для трекера привычек'

    def handle(self, *args, **options):
        self.stdout.write('Starting Telegram bot...')

        try:
            bot = HabitTrackerBot()

            # Запускаем бота в asyncio event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Если loop уже запущен (например, в Django 4.x+)
                loop.create_task(bot.run())
            else:
                # Для Django 3.x и старых версий
                loop.run_until_complete(bot.run())

        except Exception as e:
            logger.error(f"Bot error: {e}")
            self.stdout.write(self.style.ERROR(f'Bot error: {e}'))