import logging

import requests
from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.INFO)


def send_habit_reminder(chat_id, message):
    """Синхронная отправка сообщения в Telegram с подробным логированием"""
    logger.info("=== НАЧАЛО ОТПРАВКИ TELEGRAM СООБЩЕНИЯ ===")
    logger.info(f"Chat ID: {chat_id}")
    logger.info(f"Message: {message}")

    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN не настроен!")
        return False

    logger.info("✅ TELEGRAM_BOT_TOKEN найден")

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}

    logger.info(f"URL: {url}")
    logger.info(f"Payload: {payload}")

    try:
        logger.info("🔄 Отправка запроса к Telegram API...")
        response = requests.post(url, json=payload, timeout=10)
        logger.info(f"✅ Ответ получен. Status code: {response.status_code}")
        logger.info(f"📨 Response text: {response.text}")

        if response.status_code == 200:
            logger.info("🎉 Сообщение успешно отправлено!")
            return True
        else:
            logger.error(f"❌ Ошибка Telegram API: {response.status_code}")
            logger.error(f"📝 Детали: {response.text}")
            return False
    except Exception as e:
        logger.error(f"💥 Ошибка при отправке запроса: {e}")
        return False


@shared_task
def send_habit_reminder_task(habit_id):
    """Celery задача для отправки напоминания о привычке"""

    from .models import Habit

    # User = get_user_model()

    try:
        habit = Habit.objects.get(id=habit_id)
        user = habit.user

        if not user.telegram_chat_id or not user.telegram_notifications:
            return "❌ У пользователя отключены уведомления или не привязан Telegram"

        message = (
            f"⏰ <b>Напоминание о привычке!</b>\n\n"
            f"Пришло время выполнить: <b>{habit.action}</b>\n"
            f"🕐 Время: {habit.time.strftime('%H:%M')}\n"
            f"📍 Место: {habit.place}\n"
            f"⏱ Длительность: {habit.duration} секунд"
        )

        success = send_habit_reminder(user.telegram_chat_id, message)

        if success:
            return f"✅ Напоминание отправлено для: {habit.action}"
        else:
            return "❌ Ошибка при отправке напоминания"

    except Habit.DoesNotExist:
        return "❌ Привычка не найдена"
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"


@shared_task
def debug_task():
    """Самая простая задача для тестирования"""
    logger.info("=== ВЫПОЛНЕНИЕ DEBUG TASK ===")
    return "🎉 Debug task executed!"


@shared_task
def send_test_notification():
    """Отправка тестового уведомления с подробным логированием"""
    logger.info("=== НАЧАЛО ОТПРАВКИ ТЕСТОВОГО УВЕДОМЛЕНИЯ ===")

    # Находим первого пользователя с Telegram
    user = User.objects.filter(telegram_chat_id__isnull=False).first()

    if not user:
        logger.error("❌ Не найден пользователь с telegram_chat_id")
        return "❌ No users with Telegram"

    logger.info(f"✅ Найден пользователь: {user.username}")
    logger.info(f"📱 Chat ID: {user.telegram_chat_id}")
    logger.info(f"🔔 Уведомления включены: {user.telegram_notifications}")

    if not user.telegram_notifications:
        logger.warning("⚠️ Уведомления отключены у пользователя")

    message = (
        "🧪 <b>Тестовое уведомление!</b>\n\n"
        "Это сообщение пришло через систему уведомлений.\n"
        "✅ Все работает корректно!\n\n"
        "💪 Теперь вы будете получать напоминания о привычках!"
    )

    logger.info("🔄 Вызов функции отправки сообщения...")
    success = send_habit_reminder(user.telegram_chat_id, message)

    if success:
        logger.info("🎉 Задача выполнена успешно!")
        return "✅ Тестовое уведомление отправлено!"
    else:
        logger.error("❌ Задача завершилась с ошибкой")
        return "❌ Ошибка при отправке уведомления"


@shared_task
def check_and_send_habit_reminders():
    """Периодическая задача для проверки и отправки напоминаний о привычках"""
    import logging
    import pytz
    from django.utils import timezone

    from .models import Habit

    logger = logging.getLogger(__name__)
    # User = get_user_model()

    logger.info("=== 🔍 ЗАПУСК ПРОВЕРКИ НАПОМИНАНИЙ О ПРИВЫЧКАХ ===")

    # Текущее время в Москве
    moscow_tz = pytz.timezone("Europe/Moscow")
    now_moscow = timezone.now().astimezone(moscow_tz)
    current_time_moscow = now_moscow.time()

    logger.info(f"Текущее время Москва: {current_time_moscow}")

    # Все привычки пользователей с Telegram
    habits_to_check = Habit.objects.filter(
        user__telegram_chat_id__isnull=False,
        user__telegram_notifications=True,
    )

    logger.info(f"Привычек для проверки: {habits_to_check.count()}")

    results = []

    for habit in habits_to_check:
        try:
            # Время привычки в базе - это московское время (просто TimeField)
            habit_time_moscow = habit.time

            # Сравниваем время
            time_diff = abs(
                (current_time_moscow.hour * 60 + current_time_moscow.minute)
                - (habit_time_moscow.hour * 60 + habit_time_moscow.minute)
            )

            logger.info(f"Проверка: {habit.action} в {habit_time_moscow}")
            logger.info(f"Разница с текущим {current_time_moscow}: {time_diff} мин")

            if time_diff <= 2:  # ±2 минуты
                message = (
                    f"⏰ <b>Время выполнить привычку!</b>\n\n"
                    f"<b>{habit.action}</b>\n"
                    f"🕐 Время: {habit_time_moscow.strftime('%H:%M')}\n"
                    f"📍 Место: {habit.place}\n"
                    f"⏱ Длительность: {habit.duration} секунд\n"
                )

                if habit.reward:
                    message += f"🎁 Вознаграждение: {habit.reward}\n"
                elif habit.related_habit:
                    message += f"🔗 Связанная привычка: {habit.related_habit.action}\n"

                message += "\n💪 Удачи в выполнении!"

                success = send_habit_reminder(habit.user.telegram_chat_id, message)

                if success:
                    results.append(f"✅ Напоминание отправлено: {habit.action}")
                    logger.info("✅ УСПЕХ: Напоминание отправлено!")
                else:
                    results.append(f"❌ Ошибка отправки: {habit.action}")

        except Exception as e:
            error_msg = f"❌ Ошибка: {str(e)}"
            results.append(error_msg)
            logger.error(error_msg)

    return "\n".join(results) if results else "ℹ️ Напоминаний не найдено"
