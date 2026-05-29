from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from interviews.models import InterviewSession, Badge

@login_required
def dashboard(request):
    # get completed sessions first then slice
    all_sessions = InterviewSession.objects.filter(user=request.user).order_by('-created_at')
    sessions = all_sessions[:10]
    completed_sessions = all_sessions.filter(status='completed')
    badges = Badge.objects.filter(user=request.user)

    avg_score = 0
    if completed_sessions.exists():
        scores = [s.overall_score for s in completed_sessions if s.overall_score]
        if scores:
            avg_score = round(sum(scores) / len(scores), 1)

    return render(request, 'dashboard/dashboard.html', {
        'sessions': sessions,
        'completed_count': completed_sessions.count(),
        'avg_score': avg_score,
        'badges': badges,
        'xp_points': request.user.xp_points,
        'streak': request.user.streak_count,
    })