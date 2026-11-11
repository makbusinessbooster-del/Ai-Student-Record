import os
from groq import Groq


def get_api_key():
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key or key == "your_actual_groq_api_key":
        raise RuntimeError("Groq API key is missing. Add your key to the .env file, then restart the app.")
    return key


def choose_model(client):
    configured = os.getenv("GROQ_MODEL", "").strip()
    if configured:
        return configured
    try:
        available = client.models.list()
        ignored = ("whisper", "embed", "guard", "tts", "speech")
        candidates = [
            model.id for model in available.data
            if not any(word in model.id.lower() for word in ignored)
        ]
        if candidates:
            return candidates[0]
    except Exception:
        pass
    raise RuntimeError("No model is configured and Groq did not return an available text model. Set GROQ_MODEL in .env.")


def describe_student(student):
    # Deliberately excludes the student's name and ID to protect privacy.
    return {
        "class_or_semester": student["class"],
        "subjects_and_marks": student["marks"],
        "total_marks": student["total"],
        "average_percentage": student["average"],
        "grade": student["grade"],
    }


def ask_ai(prompt):
    try:
        client = Groq(api_key=get_api_key())
        model = choose_model(client)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a supportive academic assistant for teachers. "
                        "Give clear, practical, age-appropriate advice. Do not invent student details."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1000,
        )
        answer = response.choices[0].message.content
        if not answer or not answer.strip():
            raise RuntimeError("The AI returned an empty answer. Please try again.")
        return answer.strip()
    except RuntimeError:
        raise
    except Exception as exc:
        status = getattr(exc, "status_code", None)
        if status == 401:
            message = "Groq rejected the API key. Check GROQ_API_KEY in your .env file."
        elif status == 404:
            message = "The selected Groq model was not found. Check GROQ_MODEL in your .env file."
        elif status == 429:
            message = "Groq rate limit or usage limit reached. Please wait and try again."
        else:
            message = "Could not reach Groq. Check your internet connection, API key, and model name."
        raise RuntimeError(message) from exc


def analyze_performance(student):
    details = describe_student(student)
    prompt = (
        "Analyze this student's academic performance using only this information:\n"
        f"{details}\n\n"
        "Write: (1) a short overall summary, (2) strongest subjects, "
        "(3) subjects needing improvement, and (4) practical improvement actions. "
        "Be encouraging and specific. Do not request or infer the student's name or ID."
    )
    return ask_ai(prompt)


def generate_study_tips(student):
    details = describe_student(student)
    prompt = (
        "Create personalized study guidance based only on this academic information:\n"
        f"{details}\n\n"
        "Include: (1) a simple seven-day weekly study plan, (2) ways to improve weaker subjects, "
        "(3) daily study tips, (4) practical learning methods, and (5) a short motivational message. "
        "Keep the plan realistic and easy to follow. Do not request or infer the student's name or ID."
    )
    return ask_ai(prompt)
