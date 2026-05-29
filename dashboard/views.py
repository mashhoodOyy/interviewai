from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from interviews.models import InterviewSession, Badge
import json

@login_required
def dashboard(request):
    all_sessions = InterviewSession.objects.filter(user=request.user).order_by('-created_at')
    sessions = all_sessions[:10]
    completed_sessions = all_sessions.filter(status='completed')
    badges = Badge.objects.filter(user=request.user)

    avg_score = 0
    if completed_sessions.exists():
        scores = [s.overall_score for s in completed_sessions if s.overall_score]
        if scores:
            avg_score = round(sum(scores) / len(scores), 1)

    # chart data — last 10 completed sessions oldest first
    chart_sessions = list(completed_sessions.order_by('created_at')[:10])
    chart_labels = [s.created_at.strftime('%b %d') for s in chart_sessions]
    chart_scores = [s.overall_score for s in chart_sessions]

    return render(request, 'dashboard/dashboard.html', {
        'sessions': sessions,
        'completed_count': completed_sessions.count(),
        'avg_score': avg_score,
        'badges': badges,
        'xp_points': request.user.xp_points,
        'streak': request.user.streak_count,
        'chart_labels': json.dumps(chart_labels),
        'chart_scores': json.dumps(chart_scores),
    })