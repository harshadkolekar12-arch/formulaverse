"""
Django management command: audits every Formula row for content
quality issues before a distribution push. Run with:

    python manage.py audit_formulas

Checks per formula:
  1. Missing diagram_url file (field empty, or points to a file that
     doesn't exist on disk)
  2. Missing derivation_image file (same check)
  3. Suspicious LaTeX in `form` — doubled backslashes, \text{}, or
     other patterns that are known to break the mathtext renderer
  4. Empty when_to_use / mnemonic / example / common_mistakes — these
     aren't fatal but are worth knowing about for a "complete
     content" pass

Outputs a clean per-chapter breakdown, sorted worst-first, so you
know exactly where to spend your admin time.
"""
import os
import re

from django.core.management.base import BaseCommand
from django.conf import settings

from formulas.models import Formula, Chapter


SUSPICIOUS_LATEX_PATTERNS = [
    (r'\\{2,}', "doubled/tripled backslash (likely mis-escaped)"),
    (r'\\text\{', "\\text{} — not supported by mathtext renderer"),
    (r'\\begin\{', "\\begin{...} — LaTeX environment, not supported"),
    (r'\\mathrm\{', "\\mathrm{} — inconsistently supported"),
]


class Command(BaseCommand):
    help = "Audit all formulas for missing diagrams, derivations, and suspicious LaTeX."

    def add_arguments(self, parser):
        parser.add_argument(
            '--chapter',
            type=str,
            default=None,
            help='Limit audit to a single chapter name (case-insensitive).',
        )

    def handle(self, *args, **options):
        chapter_filter = options.get('chapter')

        formulas = Formula.objects.select_related('chapter').order_by(
            'chapter__name', 'id'
        )
        if chapter_filter:
            formulas = formulas.filter(chapter__name__iexact=chapter_filter)

        if not formulas.exists():
            self.stdout.write(self.style.ERROR("No formulas found."))
            return

        issues_by_chapter = {}
        total_issues = 0

        for f in formulas:
            chapter_name = f.chapter.name if f.chapter else "(no chapter)"
            problems = self._check_formula(f)
            if problems:
                issues_by_chapter.setdefault(chapter_name, []).append(
                    (f.id, f.title, problems)
                )
                total_issues += 1

        if not issues_by_chapter:
            self.stdout.write(self.style.SUCCESS(
                "\n✅ No issues found across all formulas. Content audit clean.\n"
            ))
            return

        self.stdout.write(self.style.WARNING(
            f"\n{'='*70}\n"
            f"CONTENT AUDIT — {total_issues} formula(s) with issues, "
            f"across {len(issues_by_chapter)} chapter(s)\n"
            f"{'='*70}\n"
        ))

        # Sort chapters by issue count, worst first
        sorted_chapters = sorted(
            issues_by_chapter.items(), key=lambda kv: -len(kv[1])
        )

        for chapter_name, entries in sorted_chapters:
            self.stdout.write(self.style.MIGRATE_HEADING(
                f"\n{chapter_name.upper()} — {len(entries)} formula(s) with issues"
            ))
            for formula_id, title, problems in entries:
                self.stdout.write(f"  [#{formula_id}] {title}")
                for p in problems:
                    self.stdout.write(f"      - {p}")

        self.stdout.write(self.style.WARNING(
            f"\n{'='*70}\n"
            f"Total: {total_issues} formulas need attention.\n"
            f"Fix these in Django admin, then re-run this command to confirm.\n"
            f"{'='*70}\n"
        ))

    def _check_formula(self, f):
        problems = []

        # --- Diagram check ---
        if not self._file_field_ok(f.diagram_url):
            if not f.diagram_url or not getattr(f.diagram_url, 'name', None):
                problems.append("MISSING diagram (no file uploaded)")
            else:
                problems.append(
                    f"BROKEN diagram (file uploaded but not found on disk: {f.diagram_url.name})"
                )

        # --- Derivation check ---
        if not self._file_field_ok(f.derivation_image):
            if not f.derivation_image or not getattr(f.derivation_image, 'name', None):
                problems.append("MISSING derivation image (no file uploaded)")
            else:
                problems.append(
                    f"BROKEN derivation (file uploaded but not found on disk: {f.derivation_image.name})"
                )

        # --- PDF-as-diagram/derivation check (needs rasterization) ---
        for field_name, field in [("diagram", f.diagram_url), ("derivation", f.derivation_image)]:
            if field and getattr(field, 'name', None):
                ext = os.path.splitext(field.name)[1].lower()
                if ext == '.pdf':
                    problems.append(
                        f"{field_name} is a PDF, not an image — needs rasterization to render in cheat sheet PDFs"
                    )

        # --- LaTeX sanity check on the `form` field ---
        if f.form:
            for pattern, description in SUSPICIOUS_LATEX_PATTERNS:
                if re.search(pattern, f.form):
                    problems.append(f"Suspicious LaTeX in `form`: {description}")
        else:
            problems.append("MISSING `form` (no LaTeX equation set)")

        # --- Content completeness (non-fatal, informational) ---
        empty_fields = []
        if not f.when_to_use:
            empty_fields.append("when_to_use")
        if not f.mnemonic:
            empty_fields.append("mnemonic (quick recall)")
        if not f.example:
            empty_fields.append("example (worked example)")
        if not f.common_mistakes:
            empty_fields.append("common_mistakes")
        if empty_fields:
            problems.append(f"Empty fields: {', '.join(empty_fields)}")

        return problems

    def _file_field_ok(self, field_file):
        """True if the field has a file AND it exists on disk."""
        if not field_file:
            return False
        try:
            if not field_file.name:
                return False
            return os.path.exists(field_file.path)
        except (ValueError, NotImplementedError):
            return False