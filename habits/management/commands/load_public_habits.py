import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from habits.models import Habit
from datetime import time

User = get_user_model()


class Command(BaseCommand):
    help = 'Загрузка публичных привычек в базу данных'

    def handle(self, *args, **options):
        # Создаем или получаем пользователя для публичных привычек
        user, created = User.objects.get_or_create(
            username='public_habits_bot',
            defaults={
                'email': 'bot@habittracker.com',
                'is_active': True,
                'is_verified': True
            }
        )

        if created:
            user.set_password('botpassword123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Создан пользователь для публичных привычек'))

        # Очищаем старые привычки этого пользователя
        Habit.objects.filter(user=user).delete()
        self.stdout.write('Удалены старые привычки бота')


        pleasant_habits = []
        pleasant_data = [
            {
                'action': 'Слушать любимую музыку',
                'place': 'Диван',
                'time': time(20, 30),
                'frequency': 1,
                'duration': 600,
                'is_pleasant': True
            },
            {
                'action': 'Принять ароматную ванну',
                'place': 'Ванная комната',
                'time': time(21, 0),
                'frequency': 2,
                'duration': 1800,
                'is_pleasant': True
            },
            {
                'action': 'Съесть кусочек темного шоколада',
                'place': 'Кухня',
                'time': time(16, 0),
                'frequency': 1,
                'duration': 60,
                'is_pleasant': True
            },
            {
                'action': 'Гулять 30 минут в парке',
                'place': 'Парк',
                'time': time(18, 30),
                'frequency': 1,
                'duration': 1800,
                'is_pleasant': True
            }
        ]

        for data in pleasant_data:
            habit = Habit.objects.create(
                user=user,
                **data,
                is_public=True
            )
            pleasant_habits.append(habit)
            self.stdout.write(f'Создана приятная привычка: {habit.action}')

        # Теперь создаем полезные привычки
        useful_data = [
            {
                'action': 'Пить стакан воды утром',
                'place': 'Кухня',
                'time': time(7, 0),
                'frequency': 1,
                'duration': 60,
                'reward': 'Чашка кофе'
            },
            {
                'action': 'Читать 1 страницу книги',
                'place': 'Диван',
                'time': time(21, 0),
                'frequency': 1,
                'duration': 120,
                'reward': 'Просмотр сериала'
            },
            {
                'action': 'Делать утреннюю зарядку',
                'place': 'Гостиная',
                'time': time(7, 30),
                'frequency': 1,
                'duration': 120,
                'reward': 'Контрастный душ'
            },
            {
                'action': 'Записывать 3 идеи в день',
                'place': 'Рабочий стол',
                'time': time(19, 0),
                'frequency': 1,
                'duration': 90,
                'reward': 'Вечерняя прогулка'
            },
            {
                'action': 'Медитировать 2 минуты',
                'place': 'Тихая комната',
                'time': time(8, 0),
                'frequency': 1,
                'duration': 120,
                'reward': 'Здоровый завтрак'
            },
            {
                'action': 'Планировать вечернюю прогулку',
                'place': 'Рабочий стол',
                'time': time(18, 0),
                'frequency': 1,
                'duration': 60,
                'reward': 'Свежий воздух'
            },
            {
                'action': 'Выполнять упражнение "Планка"',
                'place': 'Дома',
                'time': time(20, 0),
                'frequency': 1,
                'duration': 120,
                'reward': 'Растяжка'
            },
            {
                'action': 'Изучать 5 новых иностранных слов',
                'place': 'Рабочее место',
                'time': time(9, 0),
                'frequency': 1,
                'duration': 90,
                'reward': 'Перерыв на чай'
            },
            {
                'action': 'Составлять план на день',
                'place': 'Рабочий стол',
                'time': time(8, 30),
                'frequency': 1,
                'duration': 60,
                'reward': 'Продуктивный рабочий день'
            },
            {
                'action': 'Выполнять дыхательные упражнения',
                'place': 'Уединенное место',
                'time': time(12, 0),
                'frequency': 1,
                'duration': 120,
                'reward': 'Свежий воздух'
            },
            {
                'action': 'Проверять осанку',
                'place': 'Рабочее место',
                'time': time(10, 0),
                'frequency': 2,
                'duration': 30,
                'reward': 'Минутка отдыха'
            },
            {
                'action': 'Наполнять бутылку водой',
                'place': 'Кухня',
                'time': time(8, 0),
                'frequency': 1,
                'duration': 60,
                'reward': 'Здоровое тело'
            },
            {
                'action': 'Выполнять упражнения для глаз',
                'place': 'Рабочее место',
                'time': time(15, 0),
                'frequency': 1,
                'duration': 120,
                'reward': 'Отдых от экрана'
            },
            {
                'action': 'Планировать здоровый ужин',
                'place': 'Кухня',
                'time': time(19, 30),
                'frequency': 1,
                'duration': 120,
                'reward': 'Вкусная еда'
            },
            {
                'action': 'Писать в дневник благодарности',
                'place': 'Спальня',
                'time': time(22, 0),
                'frequency': 1,
                'duration': 120,
                'reward': 'Спокойный сон'
            }
        ]

        created_count = len(pleasant_habits)

        for data in useful_data:
            # Случайным образом решаем, будет ли у привычки связанная привычка или вознаграждение
            has_related = random.choice([True, False]) and pleasant_habits

            habit_data = {
                'user': user,
                'is_pleasant': False,
                'is_public': True,
                'related_habit': None,
                'reward': None
            }
            habit_data.update(data)

            if has_related:
                habit_data['related_habit'] = random.choice(pleasant_habits)
            else:
                habit_data['reward'] = data['reward']

            habit = Habit.objects.create(**habit_data)
            created_count += 1
            self.stdout.write(f'Создана полезная привычка: {habit.action}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Успешно создано {created_count} публичных привычек! '
                f'Теперь их можно увидеть по адресу: /habit_tracker/html/habits/public/'
            )
        )