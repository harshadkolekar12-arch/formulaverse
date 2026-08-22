from django.core.management.base import BaseCommand
from django.utils.text import slugify
from formulas.models import Formula # replace 'formulas' with your actual app name

class Command(BaseCommand):
    help = "Generate unique slugs for all Formula records that don't have one yet"

    def handle(self, *args, **kwargs):
        formulas = Formula.objects.all()
        updated_count = 0
        skipped_count = 0

        for formula in formulas:
            if formula.slug: # already has a slug, skip it
                skipped_count += 1
                continue

            base_slug = slugify(formula.title)
            slug = base_slug
            counter = 1

            # handle duplicate titles producing the same slug
            while Formula.objects.filter(slug=slug).exclude(pk=formula.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            formula.slug = slug
            formula.save()
            updated_count += 1
            self.stdout.write(f"ID {formula.id} -> {slug}")

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. {updated_count} formulas updated, {skipped_count} already had slugs."
        ))
