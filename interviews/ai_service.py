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