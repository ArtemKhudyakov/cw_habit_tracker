from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор для привычек"""

    class Meta:
        model = Habit
        fields = [
            "id",
            "user",
            "place",
            "time",
            "action",
            "is_pleasant",
            "related_habit",
            "reward",
            "frequency",
            "duration",
            "is_public",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "created_at", "updated_at"]

    def validate(self, data):
        """Дополнительная валидация на уровне сериализатора"""
        # Проверяем те же условия, что и в модели
        related_habit = data.get("related_habit")
        reward = data.get("reward")
        is_pleasant = data.get("is_pleasant", self.instance.is_pleasant if self.instance else False)

        if related_habit and reward:
            raise serializers.ValidationError("Нельзя указывать одновременно и связанную привычку, и вознаграждение")

        if related_habit and not related_habit.is_pleasant:
            raise serializers.ValidationError("В связанные привычки могут попадать только приятные привычки")

        if is_pleasant:
            if reward:
                raise serializers.ValidationError("У приятной привычки не может быть вознаграждения")
            if related_habit:
                raise serializers.ValidationError("У приятной привычки не может быть связанной привычки")

        return data

    def create(self, validated_data):
        """Автоматически назначаем текущего пользователя"""
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class PublicHabitSerializer(serializers.ModelSerializer):
    """Сериализатор для публичных привычек (только для чтения)"""

    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Habit
        fields = ["id", "user", "place", "time", "action", "frequency", "duration", "created_at"]
        read_only_fields = fields
