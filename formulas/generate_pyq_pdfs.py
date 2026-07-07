from weasyprint import HTML
import os

OUTPUT_DIR = "formulas/static/formulas/pyq_pdfs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>
    @page {{ margin: 2cm; }}
    body {{ font-family: 'Georgia', serif; color: #1a1614; font-size: 12px; }}
    .header {{ display: flex; justify-content: space-between; align-items: baseline;
               border-bottom: 2px solid #1a1614; padding-bottom: 8px; margin-bottom: 20px; }}
    .header-left h1 {{ font-size: 16px; margin: 0; }}
    .header-left p {{ font-size: 10px; color: #6b6460; margin: 2px 0 0; }}
    .header-right {{ text-align: right; font-size: 11px; }}
    .header-right .brand {{ font-weight: 700; color: #7b2d3e; }}

    .q-block {{ margin-bottom: 22px; }}
    .q-tag {{ font-size: 12px; font-weight: 700; }}
    .q-text {{ font-size: 12px; margin: 6px 0 10px; line-height: 1.6; }}
    .options-row {{ display: flex; gap: 24px; flex-wrap: wrap; margin-top: 4px; }}
    .option {{ font-size: 12px; }}

    .page-break {{ page-break-before: always; }}
    .answers-banner {{ background: #1a1614; color: white; text-align: center;
                        font-size: 13px; font-weight: 700; letter-spacing: 2px;
                        padding: 8px 0; margin-bottom: 16px; }}
    .quick-answers {{ display: flex; flex-wrap: wrap; gap: 18px; margin-bottom: 24px;
                       border-bottom: 1px solid #e8e2da; padding-bottom: 16px; }}
    .quick-answer {{ font-size: 12px; font-weight: 700; }}

    .sol-block {{ margin-bottom: 18px; font-size: 11.5px; line-height: 1.6; }}
    .sol-num {{ font-weight: 700; }}

    .footer {{ text-align: center; font-size: 10px; color: #94a3b8; margin-top: 30px; }}
    .footer .site {{ color: #38bdf8; }}
</style>
</head>
<body>

<div class="header">
    <div class="header-left">
        <h1>{chapter}</h1>
        <p>Questions with Answer Keys</p>
    </div>
    <div class="header-right">
        <div>{exam_label} — Question Bank</div>
        <div class="brand">FormulaVerse</div>
    </div>
</div>

{question_blocks}

<div class="page-break"></div>
<div class="answers-banner">ANSWERS AND SOLUTIONS</div>
<div class="quick-answers">
    {quick_answers}
</div>
{solution_blocks}

<div class="footer">
    Compiled for personal exam prep &nbsp;·&nbsp; <span class="site">formulaverse.in</span>
</div>

</body>
</html>
"""

QUESTION_BLOCK = """
<div class="q-block">
    <div class="q-tag">Q{num}. {source}</div>
    <div class="q-text">{question}</div>
    <div class="options-row">
        {options}
    </div>
</div>
"""

OPTION_SPAN = '<span class="option">({label}) {text}</span>'
QUICK_ANSWER = '<div class="quick-answer">{num}. ({answer})</div>'

SOLUTION_BLOCK = """
<div class="sol-block">
    <span class="sol-num">{num}. ({answer})</span> {solution}
</div>
"""

# ── Placeholder example data — replace with your own sourced questions ──
DATA = {
    "kinematics": {
        "chapter": "Laws of Motion",
        "exam_label": "JEE Main 2026 (January)",
        "questions": [
            {
                "source": "JEE Main 2026 (21 January Shift 2)",
                "question": "A block of mass m rests on a rough horizontal surface with coefficient of friction \u03bc. Find the minimum force required to just move the block.",
                "options": {"1": "\u03bcmg", "2": "mg/\u03bc", "3": "\u03bcmg/2", "4": "2\u03bcmg"},
                "answer": "1",
                "solution": "At the point of slipping, applied force equals maximum static friction: F = \u03bcN = \u03bcmg."
            },
            {
                "source": "JEE Main 2026 (21 January Shift 1)",
                "question": "Two blocks of mass 2 kg and 3 kg are connected by a string over a frictionless pulley. Find the acceleration of the system.",
                "options": {"1": "2 m/s\u00b2", "2": "1 m/s\u00b2", "3": "3 m/s\u00b2", "4": "4 m/s\u00b2"},
                "answer": "2",
                "solution": "Using a = (m2 - m1)g / (m1 + m2) = (3-2)(10) / 5 = 2 m/s\u00b2. Nearest matching option selected based on exact given data."
            },
        ]
    },
    # add more chapters the same way: "kinematics": {...}, "electromagnetism": {...}
}

for slug, info in DATA.items():
    q_blocks = ""
    quick_answers = ""
    sol_blocks = ""

    for i, q in enumerate(info["questions"], start=1):
        opts = "".join(OPTION_SPAN.format(label=k, text=v) for k, v in q["options"].items())
        q_blocks += QUESTION_BLOCK.format(
            num=i, source=q["source"], question=q["question"], options=opts
        )
        quick_answers += QUICK_ANSWER.format(num=i, answer=q["answer"])
        sol_blocks += SOLUTION_BLOCK.format(
            num=i, answer=q["answer"], solution=q["solution"]
        )

    html = TEMPLATE.format(
        chapter=info["chapter"],
        exam_label=info["exam_label"],
        question_blocks=q_blocks,
        quick_answers=quick_answers,
        solution_blocks=sol_blocks
    )

    filename = f"{slug}_pyq_formulas.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)
    HTML(string=html).write_pdf(filepath)
    print(f"Generated: {filename}")

print("Done.")