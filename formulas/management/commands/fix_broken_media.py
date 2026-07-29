import os
import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from formulas.models import Formula

FIELDS = ["diagram_url", "derivation_image"]


class Command(BaseCommand):
    help = "Re-download FileFields whose stored name is a raw URL, and save them as real local files."

    def handle(self, *args, **options):
        fixed, failed = 0, 0
        for f in Formula.objects.all():
            for field_name in FIELDS:
                field_file = getattr(f, field_name)
                name = field_file.name or ""
                if not name.startswith("http"):
                    continue

                self.stdout.write(f"[#{f.id}] fixing {field_name} -> {name}")
                try:
                    resp = requests.get(
                        name, timeout=15,
                        headers={"User-Agent": "formulaverse-fix/1.0"},
                    )
                    resp.raise_for_status()
                except Exception as e:
                    self.stderr.write(f"  FAILED: {e}")
                    failed += 1
                    continue

                filename = os.path.basename(name.split("?")[0]) or f"{field_name}_{f.id}.png"
                field_file.save(filename, ContentFile(resp.content), save=True)
                fixed += 1
                self.stdout.write(f"  -> saved as {field_file.name}")

        self.stdout.write(self.style.SUCCESS(f"Done. Fixed {fixed}, failed {failed}."))