from django.urls import path
from .views import (
    HabitListCreateView,
    HabitRetrieveUpdateDestroyView,
    PublicHabitListView,
    HabitListView,
    HabitDetailView,
    PublicHabitsHTMLView,
)

app_name = 'habits'

# API endpoints
api_urlpatterns = [
    path('api/habits/', HabitListCreateView.as_view(), name='api-habit-list'),
    path('api/habits/<int:pk>/', HabitRetrieveUpdateDestroyView.as_view(), name='api-habit-detail'),
    path('api/habits/public/', PublicHabitListView.as_view(), name='api-public-habits'),
]

# HTML endpoints
html_urlpatterns = [
    path('html/habits/', HabitListView.as_view(), name='html-habit-list'),
    path('html/habits/<int:pk>/', HabitDetailView.as_view(), name='html-habit-detail'),
    path('html/habits/public/', PublicHabitsHTMLView.as_view(), name='html-public-habits'),
]

# Объединяем все пути
urlpatterns = api_urlpatterns + html_urlpatterns