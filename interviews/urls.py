from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('session/new/', views.new_session, name='new_session'),
    path('session/<int:session_id>/', views.interview_room, name='interview_room'),
    path('session/<int:session_id>/results/', views.session_results, name='session_results'),
    path('daily-challenge/', views.daily_challenge, name='daily_challenge'),
    path('voice-interview/', views.voice_interview_setup, name='voice_interview_setup'),
    path('voice-interview/<int:interview_id>/', views.voice_interview_room, name='voice_interview_room'),
    path('voice-interview/<int:interview_id>/submit/', views.voice_interview_submit, name='voice_interview_submit'),
    path('voice-interview/<int:interview_id>/results/', views.voice_interview_results, name='voice_interview_results'),
]