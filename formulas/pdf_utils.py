"""
Utilities for rendering LaTeX formulas to cached PNG images, used by
the topic cheat-sheet PDF generator. Uses matplotlib's mathtext so no
system LaTeX install is required.

IMPORTANT: mathtext supports only a SUBSET of real LaTeX. Commands
like \\text{}, \\begin{cases}, \\mathrm{} (in some forms), etc. will
raise a ValueError if passed through unmodified. render_formula_png:
  1. Sanitizes the most common offending commands before rendering.
  2. Falls back to a plain (non-math) text render if mathtext still
     rejects the string, so one bad formula never crashes the whole
     PDF build.

Also includes simplify_latex_for_text(), for short mixed text+LaTeX
strings (like a one-line worked-example answer) where rendering the
whole thing as an image would look wrong — instead converts common
LaTeX macros to readable plain-text/unicode equivalents.
"""
import os
import io
import re
import hashlib

import matplotlib
matplotlib.use("Agg")  # headless, no display needed on the server
import matplotlib.pyplot as plt

from django.conf import settings


def _sanitize_latex(latex_str):
    """
    Strip/replace LaTeX commands that mathtext doesn't understand but
    that show up often enough in hand-entered formulas to be worth
    handling automatically, rather than editing every Formula row.
    """
    s = latex_str

    # Collapse stray doubled/tripled backslashes (e.g. "\\sin" -> "\sin")
    # that sometimes creep in from copy-paste or import scripts that
    # double-escape backslashes before saving to the database.
    s = re.sub(r'\\{2,}', r'\\', s)

    # \text{...} and \textrm{...} -> just the inner text
    s = re.sub(r'\\text(?:rm)?\{([^}]*)\}', r'\1', s)

    # \mathrm{...} -> keep contents, drop the wrapper
    s = re.sub(r'\\mathrm\{([^}]*)\}', r'\1', s)

    return s


def _cache_path(latex_str, fontsize, suffix=""):
    """Content-hashed filename so edits to a formula's LaTeX auto-bust the cache."""
    key = f"{latex_str}|{fontsize}|{suffix}"
    digest = hashlib.md5(key.encode("utf-8")).hexdigest()[:16]
    return os.path.join(settings.MEDIA_ROOT, "formula_png", f"{digest}.png")


def _render_png(text, fontsize, dpi, is_math):
    """Low-level render: writes `text` (as mathtext or plain text) to a PNG buffer."""
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
    """
    Render a LaTeX string (without the outer $ $) to a transparent PNG
    and return the absolute filesystem path. Cached on disk by content
    hash, so repeat calls for the same formula + fontsize are free.

    Tries mathtext first (after sanitizing common unsupported
    commands). If that still fails, falls back to rendering the raw
    string as plain text — not pretty, but never crashes the PDF.
    """
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
    """Same as render_formula_png but returns a file:// URL for use in WeasyPrint HTML."""
    path = render_formula_png(latex_str, fontsize=fontsize)
    return f"file://{path}"


# ---------------------------------------------------------------------
# Plain-text LaTeX simplification, for short mixed text+math strings
# (e.g. "Answer: \frac{350}{500}\times 100\% = 70\%") where rendering
# an image for the whole line would look out of place next to plain
# English words like "Answer:".
# ---------------------------------------------------------------------

def simplify_latex_for_text(s):
    """
    Convert common LaTeX macros to readable plain-text / unicode
    equivalents. Not a full LaTeX parser — just handles the patterns
    that show up in short hand-typed answers.
    """
    if not s:
        return s

    # \frac{a}{b} -> (a/b)
    s = re.sub(r'\\frac\{([^}]*)\}\{([^}]*)\}', r'(\1/\2)', s)

    # \sqrt{x} -> √(x)
    s = re.sub(r'\\sqrt\{([^}]*)\}', r'√(\1)', s)
    # \sqrt(x) (no braces, already parenthesized) -> √(x)
    s = re.sub(r'\\sqrt\(([^)]*)\)', r'√(\1)', s)
    # \sqrt123 (bare, no braces/parens) -> √(123)
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

    # Any remaining unhandled \commands — strip the backslash so at
    # least the word itself is still readable instead of a stray "\"
    s = re.sub(r'\\([a-zA-Z]+)', r'\1', s)

    return s