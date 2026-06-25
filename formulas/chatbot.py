from groq import Groq
from django.conf import settings
from .models import Formula
import json
import re


def get_all_formulas_text():
    formulas = Formula.objects.all()
    formula_text = ""
    for f in formulas:
        formula_text += "Title: " + str(f.title) + ", "
        formula_text += "Formula: " + str(f.form) + ", "
        formula_text += "Chapter: " + str(f.chapter) + ", "
        formula_text += "Description: " + str(f.description) + " | "
    return formula_text

def ask_chatbot(user_message, chat_history=[]):
    client = Groq(api_key=settings.GROQ_CHATBOT_KEY)
    formulas_context = get_all_formulas_text()
    system_prompt = "You are a helpful Physics tutor for Formulaverse. Help students with physics formulas and doubts. Formulas in database: " + formulas_context + " Explain simply and give real-life examples."
    messages = [{"role": "system", "content": system_prompt}]
    for msg in chat_history:
        messages.append(msg)
    messages.append({"role": "user", "content": user_message})
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=500
    )
    return response.choices[0].message.content



def generate_practice_question(formula_title, formula_eq,
                                chapter, description, difficulty="medium"):
    client = Groq(api_key=settings.GROQ_PRACTICE_KEY)

    system_prompt = """You are a physics practice question generator.
Always respond with ONLY valid JSON, no extra text."""

    user_prompt = f"""Generate a {difficulty} difficulty MCQ for this formula:
Title: {formula_title}
Formula: {formula_eq}
Chapter: {chapter}
Description: {description}

Return this exact JSON structure:
{{
    "question": "...",
    "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
    "correct": "A",
    "explanation": "..."
}}"""

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500
            )
            raw = response.choices[0].message.content.strip()
            print(f"Attempt {attempt+1} RAW GROQ RESPONSE:", raw)  # remove after debugging

            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                raw = match.group()

            result = json.loads(raw)

            if all(k in result for k in ["question", "options", "correct", "explanation"]):
                return result

        except Exception as e:
            print(f"Attempt {attempt+1} failed:", e)
            if attempt == 2:
                raise e
            continue