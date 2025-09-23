from django.core.exceptions import ValidationError


def validate_habit_duration(value, is_pleasant=False):
    """
    Валидатор для времени выполнения
    Полезная привычка: не больше 120 секунд
    Приятная привычка: без ограничений
    """
    if not is_pleasant and value > 120:
        raise ValidationError(
            "Время выполнения полезной привычки должно быть не больше 120 секунд",
            params={"value": value},
        )


def validate_habit_frequency(value):
    """Валидатор для периодичности (не реже 1 раза в 7 дней)"""
    if value > 7:
        raise ValidationError(
            "Нельзя выполнять привычку реже, чем 1 раз в 7 дней",
            params={"value": value},
        )
