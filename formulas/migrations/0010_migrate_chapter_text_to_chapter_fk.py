from django.db import migrations


def link_formulas_to_chapters(apps, schema_editor):
    Formula = apps.get_model("formulas", "Formula")
    Chapter = apps.get_model("formulas", "Chapter")

    for f in Formula.objects.all():
        raw_value = (f.chapter or "").strip()
        if not raw_value:
            continue

        chapter_obj, created = Chapter.objects.get_or_create(name=raw_value)

        # chapter is still a plain text field at this point in migration history,
        # so we store the target Chapter's id as a string for now.
        f.chapter = str(chapter_obj.id)
        f.save(update_fields=["chapter"])


def reverse_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("formulas", "0009_chapter_remove_formula_category_and_more"),
    ]

    operations = [
        migrations.RunPython(link_formulas_to_chapters, reverse_noop),
    ]