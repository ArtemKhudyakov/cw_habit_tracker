from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .validators import validate_habit_duration, validate_habit_frequency


class Habit(models.Model):
    """Модель для представления привычек пользователя"""

    # Основные поля
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="habits", verbose_name="Пользователь"
    )
    place = models.CharField(
        max_length=255, verbose_name="Место выполнения", help_text="Место, в котором необходимо выполнять привычку"
    )
    time = models.TimeField(verbose_name="Время выполнения", help_text="Время, когда необходимо выполнять привычку")
    action = models.CharField(
        max_length=255, verbose_name="Действие", help_text="Конкретное действие, которое представляет собой привычка"
    )

    # Связанные привычки и вознаграждения
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name="Признак приятной привычки",
        help_text="Является ли привычка приятной (вознаграждением)",
    )
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="related_habits",
        verbose_name="Связанная привычка",
        help_text="Приятная привычка, которая выполняется после основной",
    )
    reward = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Вознаграждение",
        help_text="Чем пользователь должен себя вознаградить после выполнения",
    )

    # Настройки выполнения
    frequency = models.PositiveIntegerField(
        default=1,
        validators=[validate_habit_frequency],
        verbose_name="Периодичность (в днях)",
        help_text="Периодичность выполнения привычки (раз в сколько дней)",
    )
    duration = models.PositiveIntegerField(
        validators=[validate_habit_duration],
        verbose_name="Время на выполнение (в секундах)",
        help_text="Время, которое предположительно потратит пользователь на выполнение привычки",
    )

    # Видимость
    is_public = models.BooleanField(
        default=False, verbose_name="Признак публичности", help_text="Могут ли другие пользователи видеть эту привычку"
    )

    # Даты для отслеживания
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}: {self.action} в {self.time}"

    def clean(self):
        """Кастомная валидация модели"""
        errors = {}

        # 1. Исключить одновременный выбор связанной привычки и указания вознаграждения
        if self.related_habit and self.reward:
            errors["reward"] = "Нельзя указывать одновременно и связанную привычку, и вознаграждение"
            errors["related_habit"] = "Нельзя указывать одновременно и связанную привычку, и вознаграждение"

        # 2. В связанные привычки могут попадать только привычки с признаком приятной привычки
        if self.related_habit and not self.related_habit.is_pleasant:
            errors["related_habit"] = "В связанные привычки могут попадать только приятные привычки"

        # 3. У приятной привычки не может быть вознаграждения или связанной привычки
        if self.is_pleasant:
            if self.reward:
                errors["reward"] = "У приятной привычки не может быть вознаграждения"
            if self.related_habit:
                errors["related_habit"] = "У приятной привычки не может быть связанной привычки"
        else:
            # 4. Время выполнения полезной привычки не больше 120 секунд
            if self.duration > 120:
                errors["duration"] = "Время выполнения полезной привычки должно быть не больше 120 секунд"

        # 5. Нельзя выполнять привычку реже, чем 1 раз в 7 дней
        if self.frequency > 7:
            errors["frequency"] = "Нельзя выполнять привычку реже, чем 1 раз в 7 дней"

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Переопределяем save для вызова полной валидации"""
        self.full_clean()
        super().save(*args, **kwargs)
