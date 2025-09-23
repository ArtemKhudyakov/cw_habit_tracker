import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from django.conf import settings
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)


class HabitTrackerBot:
    def __init__(self):
        if not settings.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN not set in settings")

        self.token = settings.TELEGRAM_BOT_TOKEN
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()

    def setup_handlers(self):
        """Настройка обработчиков команд"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("my_habits", self.my_habits))
        self.application.add_handler(CommandHandler("notifications", self.toggle_notifications))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    @sync_to_async
    def get_user_by_chat_id(self, chat_id):
        """Асинхронно получаем пользователя по chat_id"""
        try:
            return User.objects.get(telegram_chat_id=chat_id)
        except User.DoesNotExist:
            return None

    @sync_to_async
    def get_user_by_email(self, email):
        """Асинхронно получаем пользователя по email"""
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    @sync_to_async
    def save_user(self, user):
        """Асинхронно сохраняем пользователя"""
        user.save()

    @sync_to_async
    def get_user_habits(self, user):
        """Асинхронно получаем привычки пользователя"""
        from .models import Habit  # Локальный импорт чтобы избежать циклических импортов
        return list(Habit.objects.filter(user=user, is_pleasant=False))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        chat_id = update.effective_chat.id
        username = update.effective_user.username

        # Асинхронно проверяем, привязан ли уже этот chat_id
        existing_user = await self.get_user_by_chat_id(chat_id)

        if existing_user:
            await update.message.reply_text(
                f"С возвращением, {existing_user.username}! 🎉\n\n"
                f"Ваш аккаунт уже привязан.\n"
                f"Используйте /my_habits чтобы посмотреть свои привычки.\n"
                f"Используйте /notifications чтобы управлять уведомлениями."
            )
            return

        # Просим пользователя ввести email для привязки
        await update.message.reply_text(
            "👋 Добро пожаловать в Трекер Привычек!\n\n"
            "Для привязки Telegram аккаунта введите ваш email, "
            "который вы использовали при регистрации на сайте.\n\n"
            "Пример: user@example.com"
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
🤖 *Команды бота:*
/start - Начать работу с ботом
/my_habits - Показать мои привычки
/notifications - Включить/выключить уведомления
/help - Показать это сообщение

📋 *Как это работает:*
1. Бот будет присылать напоминания о ваших привычках
2. Все данные синхронизируются с вашим аккаунтом на сайте

💡 *Для привязки аккаунта просто введите ваш email*
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def my_habits(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать привычки пользователя"""
        chat_id = update.effective_chat.id

        user = await self.get_user_by_chat_id(chat_id)
        if not user:
            await update.message.reply_text(
                "❌ Ваш аккаунт не привязан. Введите ваш email для привязки."
            )
            return

        habits = await self.get_user_habits(user)

        if habits:
            message = "📋 *Ваши привычки:*\n\n"
            for habit in habits:
                message += f"🎯 *{habit.action}*\n"
                message += f"   ⏰ {habit.time.strftime('%H:%M')}\n"
                message += f"   📍 {habit.place}\n"
                message += f"   🔄 раз в {habit.frequency} дней\n\n"
        else:
            message = "У вас пока нет привычек. Создайте их на сайте! 🌟"

        await update.message.reply_text(message, parse_mode='Markdown')

    async def toggle_notifications(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Включить/выключить уведомления"""
        chat_id = update.effective_chat.id

        user = await self.get_user_by_chat_id(chat_id)
        if not user:
            await update.message.reply_text(
                "❌ Ваш аккаунт не привязан. Введите ваш email для привязки."
            )
            return

        user.telegram_notifications = not user.telegram_notifications
        await self.save_user(user)

        status = "включены" if user.telegram_notifications else "выключены"
        await update.message.reply_text(
            f"🔔 Уведомления {status}!\n"
            f"Теперь вы {'будете' if user.telegram_notifications else 'не будете'} получать напоминания о привычках."
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений (для привязки по email)"""
        chat_id = update.effective_chat.id
        text = update.message.text.strip()
        telegram_username = update.effective_user.username

        # Проверяем, является ли сообщение email'ом
        if '@' in text and ' ' not in text:  # Простая проверка на email
            # Проверяем, не привязан ли уже этот chat_id
            existing_user = await self.get_user_by_chat_id(chat_id)
            if existing_user:
                await update.message.reply_text(
                    f"❌ Ваш аккаунт уже привязан к пользователю {existing_user.username}.\n"
                    f"Используйте /my_habits чтобы посмотреть свои привычки."
                )
                return

            # Ищем пользователя по email
            user = await self.get_user_by_email(text)
            if not user:
                await update.message.reply_text(
                    "❌ Пользователь с таким email не найден.\n"
                    "Проверьте правильность email или зарегистрируйтесь на сайте."
                )
                return

            # Проверяем, не привязан ли email к другому Telegram аккаунту
            if user.telegram_chat_id:
                await update.message.reply_text(
                    "❌ Этот email уже привязан к другому Telegram аккаунту.\n"
                    "Обратитесь к администратору для решения проблемы."
                )
                return

            # Привязываем Telegram к пользователю
            user.telegram_chat_id = chat_id
            user.telegram_username = telegram_username
            await self.save_user(user)

            await update.message.reply_text(
                f"✅ Аккаунт успешно привязан!\n"
                f"Добро пожаловать, {user.username}! 🎉\n\n"
                f"Теперь вы будете получать напоминания о своих привычках.\n"
                f"Используйте /my_habits чтобы посмотреть свои привычки.\n"
                f"Используйте /notifications чтобы управлять уведомлениями."
            )
        else:
            await update.message.reply_text(
                "🤔 Не понимаю ваше сообщение.\n\n"
                "Для привязки аккаунта введите ваш email.\n"
                "Пример: user@example.com\n\n"
                "Или используйте команды:\n"
                "/help - показать справку"
            )

    def run(self):
        """Запуск бота"""
        logger.info("Starting Telegram bot...")
        self.application.run_polling()