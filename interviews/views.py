from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import InterviewSession, Question, Answer, Badge
from .ai_service import generate_questions, score_answer

def home(request):
    return render(request, 'home.html')

@login_required
def new_session(request):
    if request.method == 'POST':
        job_title = request.POST['job_title']
        company = request.POST.get('company', '')
        mode = request.POST['mode']

        # create session
        session = InterviewSession.objects.create(
            user=request.user,
            job_title=job_title,
            company=company,
            mode=mode
        )

        # generate questions using AI
        try:
            questions_data = generate_questions(
                job_title,
                company,
                request.user.experience_level,
                mode
            )

            for i, q in enumerate(questions_data):
                Question.objects.create(
                    session=session,
                    text=q['text'],
                    category=q['category'],
                    difficulty=q['difficulty'],
                    order=i + 1
                )

            messages.success(request, 'Interview session created! Good luck! 🎯')
            return redirect('interview_room', session_id=session.id)

        except Exception as e:
            session.delete()
            messages.error(request, 'Failed to generate questions. Please try again!')
            return redirect('new_session')

    return render(request, 'interviews/new_session.html')

@login_required
def interview_room(request, session_id):
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)

    if session.status == 'completed':
        return redirect('session_results', session_id=session_id)

    # get next unanswered question
    answered_ids = Answer.objects.filter(
        question__session=session
    ).values_list('question_id', flat=True)

    next_question = session.questions.exclude(id__in=answered_ids).first()

    if not next_question:
        # all questions answered — complete session
        answers = Answer.objects.filter(question__session=session)
        if answers.exists():
            avg_score = sum(a.ai_score for a in answers if a.ai_score) / answers.count()
            session.overall_score = round(avg_score, 1)
        session.status = 'completed'
        session.save()

        # award first interview badge
        Badge.objects.get_or_create(user=request.user, name='first_interview')

        # add XP
        request.user.xp_points += 100
        request.user.save()

        return redirect('session_results', session_id=session_id)

    if request.method == 'POST':
        answer_text = request.POST.get('answer', '')

        if answer_text.strip():
            # score the answer using AI
            try:
                result = score_answer(
                    next_question.text,
                    answer_text,
                    session.job_title,
                    request.user.experience_level
                )

                Answer.objects.create(
                    question=next_question,
                    text=answer_text,
                    ai_score=result['score'],
                    ai_feedback=result['feedback'],
                    improvement_tips=result['improvement_tips'],
                    ideal_answer=result['ideal_answer'],
                    filler_word_count=result['filler_word_count']
                )

                messages.success(request, f'Answer submitted! Score: {result["score"]}/10')

            except Exception as e:
                messages.error(request, 'Failed to score answer. Please try again!')

        return redirect('interview_room', session_id=session_id)

    total_questions = session.questions.count()
    answered_count = len(answered_ids)

    return render(request, 'interviews/interview_room.html', {
        'session': session,
        'question': next_question,
        'answered_count': answered_count,
        'total_questions': total_questions,
        'progress': int((answered_count / total_questions) * 100) if total_questions > 0 else 0,
    })

@login_required
def session_results(request, session_id):
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    answers = Answer.objects.filter(question__session=session).select_related('question')

    return render(request, 'interviews/session_results.html', {
        'session': session,
        'answers': answers,
    })