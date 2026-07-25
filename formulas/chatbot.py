from groq import Groq
from django.conf import settings
from .models import Formula
import json
import re
from datetime import datetime
import random, math, time


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


SAFE_FUNCS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "sqrt": math.sqrt,
    "log": math.log10,
    "ln": math.log,
    "exp": math.exp,
    "pi": math.pi,
    "e": math.e,
    "abs": abs,
    "pow": pow,
}


def safe_eval(expr: str) -> float:
    """
    Evaluate a restricted math expression string (e.g. '2*sin(4*2 - 0.5*3)').
    Raises on anything unexpected -- caller should catch and reject the attempt.
    """
    if not isinstance(expr, str) or not expr.strip():
        raise ValueError("Empty or invalid calculation_expression")

    # Reject anything that looks like it's trying to escape the sandbox
    if re.search(r'(__|import|lambda|;|\[|\]|=[^=])', expr):
        raise ValueError(f"Unsafe expression rejected: {expr}")

    return float(eval(expr, {"_builtins_": {}}, SAFE_FUNCS))


def extract_number(text: str):
    """
    Pull the first numeric value out of an option string like '0.46 cm' or '-1.37 cm'.
    Returns None if no number is found.
    """
    if not isinstance(text, str):
        return None
    match = re.search(r'-?\d+\.?\d*(?:[eE][-+]?\d+)?', text)
    return float(match.group()) if match else None


def values_match(computed: float, stated: float, rel_tol: float = 0.05, abs_tol: float = 0.01) -> bool:
    """
    Compare computed vs. model-stated numeric answer with a tolerance band,
    since rounding/unit-display differences are expected and fine.
    """
    return math.isclose(computed, stated, rel_tol=rel_tol, abs_tol=abs_tol)


# ---------------------------------------------------------------------------
# GROQ MODEL CHAIN
# ---------------------------------------------------------------------------
# Tried in order. If one model is congested/erroring, we hop to the next
# instead of hammering the same queue repeatedly.
MODEL_CHAIN = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "llama-3.3-70b-versatile",
]

# How many attempts to spend on a single model before moving to the next one.
# Total attempts = ATTEMPTS_PER_MODEL * len(MODEL_CHAIN).
ATTEMPTS_PER_MODEL = 2


def _groq_client():
    return Groq(
        api_key=settings.GROQ_PRACTICE_KEY,
        timeout=15.0,      # don't let a hung request block silently for 60s+
        max_retries=0,     # we handle retries/backoff ourselves below
    )


# ---------------------------------------------------------------------------
# MAIN GENERATOR
# ---------------------------------------------------------------------------
SCENARIOS = [
    "space flight or satellite telemetry",
    "automotive transport engineering",
    "laboratory experimental setups",
    "sports mechanics or athletic kinematics",
]

AI_DISCLAIMER = (
    "\n\n Note: This problem is AI-generated. Please verify the steps and "
    "final calculations independently."
)


def build_system_prompt(formula_eq: str) -> str:
    return f"""You are an elite, mathematically rigorous physics examination writer for FormulaVerse.
Your goal is to output a perfect multiple-choice question without any math contradictions or formatting errors.

CRITICAL FORMATTING & MATH RULES:
1. NO RAW BACKSLASHES: Do not use LaTeX symbols like '\\frac' or '\\Delta' in the JSON because backslashes break JSON string decoding. Instead, write fractions cleanly as '1/2' and changes as 'Delta' or 'change in'. Use standard text characters (e.g., '^2' for squared, '*' for multiplication).
2. SOLVE FIRST: Assign simple whole numbers to the variables for the formula: {formula_eq}. Solve it completely step-by-step internally before building options.
3. DOUBLE-CHECK WRONG OPTIONS: Make sure the true calculated answer matches your specified correct option letter exactly. Verify that your distractors do not accidentally equal the correct value.
4. PROVIDE A COMPUTABLE EXPRESSION: You must also provide "calculation_expression" -- a pure, Python-evaluable math expression (numbers and functions only: sin, cos, tan, sqrt, log, ln, exp, pi -- no variable names, no units, no '=' signs) that evaluates to the exact numeric value of the correct option. This will be independently re-computed and checked against your stated answer, so it must be accurate.

You must respond ONLY with a valid JSON object matching the requested structure. Do not include markdown code block backticks or conversational filler."""


def build_user_prompt(formula_title, formula_eq, chapter, description, difficulty, scenario) -> str:
    return f"""Generate an entirely unique {difficulty} difficulty physics MCQ based around this context setting: {scenario}.

FORMULA DATA CONTEXT:
Title: {formula_title}
Formula: {formula_eq}
Chapter: {chapter}
Description: {description}

Return ONLY this exact JSON structure:
{{
    "question": "The conceptual text question...",
    "options": {{
        "A": "Option text or exact numerical value with units",
        "B": "Option text or exact numerical value with units",
        "C": "Option text or exact numerical value with units",
        "D": "Option text or exact numerical value with units"
    }},
    "correct": "The absolute correct option letter, must be exactly 'A', 'B', 'C', or 'D'",
    "calculation_expression": "A pure Python-evaluable math expression using only numbers and sin/cos/tan/sqrt/log/ln/exp/pi. Example: 2*sin(4*2 - 0.5*3). No variable names, no units, no '=' signs.",
    "explanation": "A breakdown of the numbers chosen, substitution step-by-step, and final calculation."
}}"""


def _call_model(client, model_name, system_prompt, user_prompt):
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=800,
        temperature=0.1,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content.strip()


def generate_practice_question(formula_title, formula_eq, chapter, description, difficulty="medium"):
    client = _groq_client()

    chosen_scenario = random.choice(SCENARIOS)
    system_prompt = build_system_prompt(formula_eq)
    user_prompt = build_user_prompt(
        formula_title, formula_eq, chapter, description, difficulty, chosen_scenario
    )

    last_error = None
    global_attempt = 0

    for model_name in MODEL_CHAIN:
        for local_attempt in range(1, ATTEMPTS_PER_MODEL + 1):
            global_attempt += 1
            try:
                raw = _call_model(client, model_name, system_prompt, user_prompt)
                print(f"[{model_name} attempt {local_attempt}] RAW GROQ RESPONSE:", raw)

                # In case the model wraps JSON in stray text despite instructions
                match = re.search(r'\{.*\}', raw, re.DOTALL)
                if match:
                    raw = match.group()

                result = json.loads(raw)

                required_keys = ["question", "options", "correct", "explanation", "calculation_expression"]
                if not all(k in result for k in required_keys):
                    print(f"[{model_name} attempt {local_attempt}] Missing required keys, retrying.")
                    continue

                if result["correct"] not in result["options"]:
                    print(f"[{model_name} attempt {local_attempt}] 'correct' letter not found in options, retrying.")
                    continue

                # --- Independent verification step -------------------------------
                try:
                    computed_value = safe_eval(result["calculation_expression"])
                except Exception as calc_err:
                    print(f"[{model_name} attempt {local_attempt}] calculation_expression failed to evaluate: {calc_err}")
                    continue

                stated_text = result["options"][result["correct"]]
                stated_value = extract_number(stated_text)

                if stated_value is None:
                    print(f"[{model_name} attempt {local_attempt}] Could not extract a number from correct option: {stated_text!r}")
                    continue

                if not values_match(computed_value, stated_value):
                    print(
                        f"[{model_name} attempt {local_attempt}] MISMATCH -- independently computed "
                        f"{computed_value}, model's stated correct option = {stated_value}. Rejecting."
                    )
                    continue

                # Passed verification -- safe to ship
                result["explanation"] = result["explanation"] + AI_DISCLAIMER
                print(f"[{model_name} attempt {local_attempt}] Verified OK: computed={computed_value}, stated={stated_value}")
                return result

            except Exception as e:
                last_error = e
                print(f"[{model_name} attempt {local_attempt}] failed with exception: {e}")
                # Small jittered backoff so we don't immediately re-hit a congested queue
                time.sleep(min(2 ** local_attempt, 6) + random.uniform(0, 0.5))
                continue

        print(f"[{model_name}] exhausted {ATTEMPTS_PER_MODEL} attempts, hopping to next model.")

    raise ValueError(
        f"Failed to generate a verified question for '{formula_title}' "
        f"after {global_attempt} attempts across all models. Last error: {last_error}"
    )


def get_daily_physics_fact():
    """
    Fetches a compelling historical physics fact for the current day
    using Groq and Llama.
    """
    # Get current date string (e.g., "July 08")
    current_date = datetime.now().strftime("%B %d")
    client = Groq(api_key=settings.GROQ_FACTS_KEY)

    system_prompt = """You are a rigorous Physics historian engine for FormulaVerse. Your ONLY job is to return one historically verified physics fact - a discovery, event, or scientist's birth/death - that occurred on the EXACT calendar date provided (matching both day and month precisely).

STRICT VERIFICATION RULES:
1. Before answering, internally verify the exact day AND month of the fact. Do not rely on approximate memory - if you are not fully certain the date is correct, discard that fact and consider a different one.
2. Never guess or estimate a date to make a "good story" fit. Accuracy on the exact date is more important than fame of the scientist or discovery.
3. If you cannot recall any physics fact you are fully confident occurred on this exact date, respond with exactly: NO_VERIFIED_FACT
   Do not fabricate one to fill the space.
4. Double-check that any date icon, emoji, or label you include in the output matches the same date as the text - never let these contradict each other.
5. Prefer well-documented, globally significant milestones (e.g. Newton, Einstein, Curie, Bohr, Chadwick, Euler, Planck, Faraday) ONLY when their date is exactly correct - fame is not a substitute for date accuracy.

OUTPUT FORMAT (only if a verified fact exists):
On This Day: [Brief 1-line title]
[A captivating, 2-3 sentence description explaining the science and why it matters to students.]

If no verified fact exists for the given date, output only: NO_VERIFIED_FACT
"""

    user_prompt = f"Today's date is {current_date}. Give me an interesting physics fact for this exact date."

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=200
        )
        return completion.choices[0].message.content
    except Exception as e:
        # Fallback safety content in case your API hits a network glitch or rate limit
        return (
            "📅 On This Day: Exploring the Multiverse!\n"
            "📜 Great discoveries are happening every second. Dive into your formula dashboards "
            "and create your own physics milestones today!"
        )




