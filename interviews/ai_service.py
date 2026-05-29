import json
from groq import Groq
from django.conf import settings

client = Groq(api_key=settings.GROQ_API_KEY)

def generate_questions(job_title, company, experience_level, mode):
    if mode == 'quick':
        num_questions = 5
    elif mode == 'full':
        num_questions = 10
    else:
        num_questions = 7

    prompt = f"""You are an expert interviewer. Generate {num_questions} interview questions for:
- Job Title: {job_title}
- Company: {company if company else 'a typical company'}
- Experience Level: {experience_level}

Generate a mix of behavioral, technical, situational and culture fit questions.

Return ONLY a JSON array, no other text, no markdown, no backticks:
[
    {{
        "text": "question here",
        "category": "behavioral",
        "difficulty": "medium"
    }}
]

Categories must be one of: behavioral, technical, situational, culture_fit
Difficulty must be one of: easy, medium, hard"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1000,
    )

    response_text = response.choices[0].message.content
    questions = json.loads(response_text)
    return questions


def score_answer(question_text, answer_text, job_title, experience_level):
    prompt = f"""You are an expert interview coach. Evaluate this interview answer.

Job Title: {job_title}
Experience Level: {experience_level}
Question: {question_text}
Answer: {answer_text}

Return ONLY this JSON, no other text, no markdown, no backticks:
{{
    "score": 7.5,
    "feedback": "Overall feedback here",
    "improvement_tips": "Specific tips to improve",
    "ideal_answer": "What a great answer would look like",
    "filler_word_count": 2
}}

Score must be between 0 and 10.
filler_word_count is how many filler words (um, uh, like, you know, basically) appear in the answer."""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=1000,
    )

    response_text = response.choices[0].message.content
    result = json.loads(response_text)
    return result

def analyze_resume(resume_text, target_role, experience_level):
    prompt = f"""You are an expert career coach and resume reviewer.

Analyze this resume for someone targeting: {target_role}
Experience Level: {experience_level}

Resume Content:
{resume_text[:3000]}

Return ONLY this JSON, no other text, no markdown, no backticks:
{{
    "overall_score": 7.5,
    "summary": "Brief overall assessment",
    "strengths": ["strength 1", "strength 2", "strength 3"],
    "weaknesses": ["weakness 1", "weakness 2"],
    "missing_skills": ["skill 1", "skill 2", "skill 3"],
    "improvement_tips": ["tip 1", "tip 2", "tip 3"],
    "ats_score": 8.0,
    "ats_tips": ["ats tip 1", "ats tip 2"]
}}

overall_score: rate resume quality 0-10
ats_score: how well it passes ATS systems 0-10
missing_skills: skills needed for {target_role} that are missing from resume"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=1000,
    )

    response_text = response.choices[0].message.content
    result = json.loads(response_text)
    return result