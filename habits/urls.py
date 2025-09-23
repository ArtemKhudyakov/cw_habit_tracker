from django.urls import path
from .views import (
    HabitListCreateView,
    HabitRetrieveUpdateDestroyView,
    PublicHabitListView,
    HabitListView,
    HabitDetailView,
    PublicHabitsHTMLView,
    NotificationsView,
    SendTestNotificationView,
    TestHabitReminderView,
    ToggleNotificationsView,
)

app_name = 'habits'

# API endpoints
api_urlpatterns = [
    path('api/habits/', HabitListCreateView.as_view(), name='api-habit-list'),
    path('api/habits/<int:pk>/', HabitRetrieveUpdateDestroyView.as_view(), name='api-habit-detail'),
    path('api/habits/public/', PublicHabitListView.as_view(), name='api-public-habits'),
    path('api/notifications/test/', SendTestNotificationView.as_view(), name='send_test_notification'),
    path('api/notifications/test-habit/', TestHabitReminderView.as_view(), name='test_habit_reminder'),
    path('api/notifications/toggle/', ToggleNotificationsView.as_view(), name='toggle_notifications'),
]

# HTML endpoints
html_urlpatterns = [
    path('html/habits/', HabitListView.as_view(), name='html-habit-list'),
    path('html/habits/<int:pk>/', HabitDetailView.as_view(), name='html-habit-detail'),
    path('html/habits/public/', PublicHabitsHTMLView.as_view(), name='html-public-habits'),
    path('html/notifications/', NotificationsView.as_view(), name='notifications'),
]

# Объединяем все пути
urlpatterns = api_urlpatterns + html_urlpatterns
