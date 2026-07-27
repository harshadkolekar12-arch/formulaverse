"""
Utilities for rendering LaTeX formulas to cached PNG images, used by
the topic cheat-sheet PDF generator. Uses matplotlib's mathtext so no
system LaTeX install is required.
"""
import os
import io
import hashlib
import re
import matplotlib
matplotlib.use("Agg")  # headless, no display needed on the server
import matplotlib.pyplot as plt

from django.conf import settings


def _cache_path(latex_str, fontsize):
    """Content-hashed filename so edits to a formula's LaTeX auto-bust the cache."""
    key = f"{latex_str}|{fontsize}"
    digest = hashlib.md5(key.encode("utf-8")).hexdigest()[:16]
    return os.path.join(settings.MEDIA_ROOT, "formula_png", f"{digest}.png")


def render_formula_png(latex_str, fontsize=26, dpi=300):
    if not latex_str:
        latex_str = ""

    # 1. Clean up escaping and extra dollars/whitespace
    latex_str = latex_str.strip().strip("$")
    latex_str = latex_str.replace("\\\\", "\\")

    # 2. Convert unsupported amsmath commands to Matplotlib equivalents
    latex_str = latex_str.replace("\\lvert", "|").replace("\\rvert", "|")
    latex_str = latex_str.replace("\\Vert", "|").replace("\\vert", "|")

    # 3. Fix \sqrt(...) syntax to \sqrt{...}
    latex_str = re.sub(r'\\sqrt\s*\((.*?)\)', r'\\sqrt{\1}', latex_str)

    path = _cache_path(latex_str, fontsize)
    if os.path.exists(path):
        return path

    os.makedirs(os.path.dirname(path), exist_ok=True)

    fig = plt.figure(figsize=(0.01, 0.01))
    fig.patch.set_alpha(0.0)
    fig.text(0, 0, f"${latex_str}$", fontsize=fontsize, color="#111111")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight', pad_inches=0.08, transparent=True, dpi=dpi)
    plt.close(fig)
    plt.close('all')

    with open(path, "wb") as f:
        f.write(buf.getvalue())

    return path


def render_formula_media_url(latex_str, fontsize=26):
    """Same as render_formula_png but returns a file:// URL for use in WeasyPrint HTML."""
    path = render_formula_png(latex_str, fontsize=fontsize)
    return f"file://{path}"