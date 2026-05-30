from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import InterviewSession, Question, Answer, Badge
from .ai_service import generate_questions, score_answer
import json as json_module
from .models import VoiceInterview, VoiceAnswer
from .ai_service import generate_voice_questions, generate_voice_report



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
        # update streak
        request.user.update_streak()

        # award streak badge if 7 days
        if request.user.streak_count >= 7:
            Badge.objects.get_or_create(user=request.user, name='streak_7')

        # award perfect score badge
        if session.overall_score and session.overall_score >= 9:
            Badge.objects.get_or_create(user=request.user, name='perfect_score')



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



@login_required
def daily_challenge(request):
    today = date.today()

    # get or create today's challenge
    challenge = DailyChallenge.objects.filter(date=today).first()

    if not challenge:
        # generate new question for today
        try:
            question_data = generate_daily_question()
            challenge = DailyChallenge.objects.create(
                question_text=question_data['text'],
                category=question_data['category'],
                date=today
            )
        except Exception as e:
            messages.error(request, 'Failed to load daily challenge. Try again!')
            return redirect('dashboard')

    # check if user already answered today
    existing_answer = DailyChallengeAnswer.objects.filter(
        challenge=challenge,
        user=request.user
    ).first()

    if request.method == 'POST' and not existing_answer:
        answer_text = request.POST.get('answer', '')
        if answer_text.strip():
            try:
                result = score_answer(
                    challenge.question_text,
                    answer_text,
                    'General Professional',
                    request.user.experience_level
                )

                DailyChallengeAnswer.objects.create(
                    challenge=challenge,
                    user=request.user,
                    answer_text=answer_text,
                    ai_score=result['score'],
                    ai_feedback=result['feedback']
                )

                # award XP
                request.user.xp_points += 25
                request.user.save()

                messages.success(request, f'Daily challenge complete! +25 XP 🎉 Score: {result["score"]}/10')
                return redirect('daily_challenge')

            except Exception as e:
                messages.error(request, 'Failed to score answer. Try again!')

    return render(request, 'interviews/daily_challenge.html', {
        'challenge': challenge,
        'existing_answer': existing_answer,
        'today': today,
    })



@login_required
def voice_interview_setup(request):
    if request.method == 'POST':
        job_title = request.POST.get('job_title', '')

        # get resume text if available
        resume_text = ''
        if request.user.resume:
            try:
                import PyPDF2
                import io
                with request.user.resume.open('rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text:
                            resume_text += text
            except:
                pass

        # generate questions
        try:
            questions = generate_voice_questions(
                job_title,
                resume_text,
                request.user.experience_level
            )

            # create voice interview session
            interview = VoiceInterview.objects.create(
                user=request.user,
                job_title=job_title
            )

            # store questions in session
            request.session['voice_questions'] = questions
            request.session['voice_interview_id'] = interview.id

            return redirect('voice_interview_room', interview_id=interview.id)

        except Exception as e:
            messages.error(request, f'Failed to generate questions: {str(e)}')

    return render(request, 'interviews/voice_setup.html')


@login_required
def voice_interview_room(request, interview_id):
    interview = get_object_or_404(VoiceInterview, id=interview_id, user=request.user)
    questions = request.session.get('voice_questions', [])

    if not questions:
        messages.error(request, 'Session expired. Please start again.')
        return redirect('voice_interview_setup')

    return render(request, 'interviews/voice_room.html', {
        'interview': interview,
        'questions_json': json_module.dumps(questions),
    })


@login_required
def voice_interview_submit(request, interview_id):
    if request.method == 'POST':
        interview = get_object_or_404(VoiceInterview, id=interview_id, user=request.user)

        data = json_module.loads(request.body)
        answers_data = data.get('answers', [])
        duration = data.get('duration', 0)

        # score each answer and save
        total_score = 0
        total_filler = 0
        saved_answers = []

        for i, item in enumerate(answers_data):
            try:
                result = score_answer(
                    item['question'],
                    item['answer'],
                    interview.job_title,
                    request.user.experience_level
                )

                VoiceAnswer.objects.create(
                    interview=interview,
                    question_text=item['question'],
                    answer_text=item['answer'],
                    ai_score=result['score'],
                    ai_feedback=result['feedback'],
                    filler_word_count=result['filler_word_count'],
                    order=i + 1
                )

                total_score += result['score']
                total_filler += result['filler_word_count']
                saved_answers.append({
                    'question': item['question'],
                    'answer': item['answer'],
                    'score': result['score']
                })

            except Exception as e:
                print(f"Error scoring answer: {e}")

        # generate full report
        try:
            report = generate_voice_report(interview.job_title, saved_answers)
            interview.overall_score = report['overall_score']
            interview.communication_score = report['communication_score']
            interview.duration_seconds = duration
            interview.status = 'completed'
            interview.save()

            # award XP
            request.user.xp_points += 150
            request.user.save()

            # clear session
            if 'voice_questions' in request.session:
                del request.session['voice_questions']

            return JsonResponse({
                'success': True,
                'redirect': f'/voice-interview/{interview_id}/results/'
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False})


@login_required
def voice_interview_results(request, interview_id):
    interview = get_object_or_404(VoiceInterview, id=interview_id, user=request.user)
    answers = VoiceAnswer.objects.filter(interview=interview)

    return render(request, 'interviews/voice_results.html', {
        'interview': interview,
        'answers': answers,
    })