import os
import io
import re
import hashlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from django.conf import settings


def _sanitize_latex(latex_str):
    s = latex_str
    s = re.sub(r'\\{2,}', r'\\', s)
    s = re.sub(r'\\text(?:rm)?\{([^}]*)\}', r'\1', s)
    s = re.sub(r'\\mathrm\{([^}]*)\}', r'\1', s)

    return s


def _cache_path(latex_str, fontsize, suffix=""):
    key = f"{latex_str}|{fontsize}|{suffix}"
    digest = hashlib.md5(key.encode("utf-8")).hexdigest()[:16]
    return os.path.join(settings.MEDIA_ROOT, "formula_png", f"{digest}.png")


def _render_png(text, fontsize, dpi, is_math):
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.patch.set_alpha(0.0)

    display_text = f"${text}$" if is_math else text
    fig.text(0, 0, display_text, fontsize=fontsize, color="#111111")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=0.08,
                transparent=True, dpi=dpi)
    plt.close(fig)
    return buf.getvalue()


def render_formula_png(latex_str, fontsize=26, dpi=300):
    path = _cache_path(latex_str, fontsize)
    if os.path.exists(path):
        return path

    os.makedirs(os.path.dirname(path), exist_ok=True)

    cleaned = _sanitize_latex(latex_str)

    try:
        png_bytes = _render_png(cleaned, fontsize, dpi, is_math=True)
    except ValueError:
        plain = re.sub(r'\\[a-zA-Z]+', '', latex_str)
        plain = plain.replace('{', '').replace('}', '')
        png_bytes = _render_png(plain, fontsize, dpi, is_math=False)

    with open(path, "wb") as f:
        f.write(png_bytes)

    return path


def render_formula_media_url(latex_str, fontsize=26):
    path = render_formula_png(latex_str, fontsize=fontsize)
    return f"file://{path}"

def _prep_answer_for_mathtext(raw_answer):
    if not raw_answer:
        return ""

    s = raw_answer.strip()
    s = s.replace("$$", "").strip()
    s = re.sub(r"^Answer:\s*", "", s, flags=re.IGNORECASE)
    s = s.replace("×", r"\times ")

    for _ in range(2):
        s = re.sub(r"\(([^()]+)\)\s*/\s*\(([^()]+)\)", r"\\frac{\1}{\2}", s)

    s = s.strip()
    if s.startswith("(") and s.endswith(")"):
        s = s[1:-1]

    return s


def render_answer_media_url(raw_answer, fontsize=22):
    cleaned = _prep_answer_for_mathtext(raw_answer)
    if not cleaned:
        return None
    return render_formula_media_url(cleaned, fontsize=fontsize)

def simplify_latex_for_text(s):
    if not s:
        return s

    s = re.sub(r'\\frac\{([^}]*)\}\{([^}]*)\}', r'(\1/\2)', s)
    s = re.sub(r'\\sqrt\{([^}]*)\}', r'√(\1)', s)
    s = re.sub(r'\\sqrt\(([^)]*)\)', r'√(\1)', s)
    s = re.sub(r'\\sqrt([0-9.]+)', r'√(\1)', s)

    replacements = {
        r'\times': '×',
        r'\cdot': '·',
        r'\pm': '±',
        r'\%': '%',
        r'\div': '÷',
        r'\approx': '≈',
        r'\ne': '≠',
        r'\leq': '≤',
        r'\geq': '≥',
        r'\infty': '∞',
        r'\pi': 'π',
        r'\theta': 'θ',
        r'\omega': 'ω',
        r'\Delta': 'Δ',
    }
    for latex, unicode_char in replacements.items():
        s = s.replace(latex, unicode_char)

    s = re.sub(r'\\([a-zA-Z]+)', r'\1', s)

    return s



_SUPERSCRIPT_MAP = {
    "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
    "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹",
    "-": "⁻", "+": "⁺",
}


def _to_unicode_superscript(s):
    def repl(match):
        exp = match.group(1)
        return "".join(_SUPERSCRIPT_MAP.get(c, c) for c in exp)

    s = re.sub(r"\^\{([^}]+)\}", repl, s)
    s = re.sub(r"\^([0-9\-])", lambda m: _SUPERSCRIPT_MAP.get(m.group(1), m.group(1)), s)
    return s


def format_units_for_display(units_str):
    if not units_str:
        return units_str

    s = simplify_latex_for_text(units_str)
    s = _to_unicode_superscript(s)
    return s