from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Habit
from .serializers import HabitSerializer, PublicHabitSerializer
from .permissions import IsOwner
from django.http import Http404


# API Views
class HabitListCreateView(generics.ListCreateAPIView):
    """API для создания и просмотра своих привычек"""
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['is_pleasant', 'is_public']
    ordering_fields = ['time', 'created_at']

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HabitRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """API для просмотра, обновления и удаления привычки"""
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)


class PublicHabitListView(generics.ListAPIView):
    """API для просмотра публичных привычек"""
    serializer_class = PublicHabitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(is_public=True).exclude(user=self.request.user)


# HTML Views
class HabitListView(LoginRequiredMixin, ListView):
    """HTML страница со списком привычек пользователя"""
    model = Habit
    template_name = 'habits/habit_list.html'
    context_object_name = 'habits'
    paginate_by = 5

    def get_queryset(self):
        queryset = Habit.objects.filter(user=self.request.user).order_by('-created_at')

        # Упрощенная фильтрация
        habit_type = self.request.GET.get('type')
        if habit_type == 'useful':
            return queryset.filter(is_pleasant=False)
        elif habit_type == 'pleasant':
            return queryset.filter(is_pleasant=True)

        return queryset


class PublicHabitsHTMLView(LoginRequiredMixin, ListView):
    """HTML страница с публичными привычками"""
    model = Habit
    template_name = 'habits/public_habits.html'
    context_object_name = 'habits'

    def get_queryset(self):
        queryset = Habit.objects.filter(is_public=True).exclude(user=self.request.user)

        # Упрощенная фильтрация
        habit_type = self.request.GET.get('type')
        if habit_type == 'useful':
            return queryset.filter(is_pleasant=False)
        elif habit_type == 'pleasant':
            return queryset.filter(is_pleasant=True)

        return queryset


class HabitDetailView(LoginRequiredMixin, DetailView):
    """HTML страница детального просмотра привычки"""
    model = Habit
    template_name = 'habits/habit_detail.html'
    context_object_name = 'habit'

    def get_queryset(self):
        """Пользователь может смотреть только свои привычки ИЛИ публичные привычки других пользователей"""
        user_habits = Habit.objects.filter(user=self.request.user)
        public_habits = Habit.objects.filter(is_public=True).exclude(user=self.request.user)
        return user_habits | public_habits

    def get_object(self, queryset=None):
        """Получаем объект с проверкой прав доступа"""
        if queryset is None:
            queryset = self.get_queryset()

        pk = self.kwargs.get('pk')
        try:
            return queryset.get(pk=pk)
        except Habit.DoesNotExist:
            raise Http404("Привычка не найдена или у вас нет доступа к ней")
