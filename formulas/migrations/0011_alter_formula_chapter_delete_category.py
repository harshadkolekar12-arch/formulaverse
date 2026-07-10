import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("formulas", "0010_migrate_chapter_text_to_chapter_fk"),
    ]

    operations = [
        migrations.AlterField(
            model_name="formula",
            name="chapter",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="formulas.chapter",
            ),
        ),
        migrations.DeleteModel(
            name="Category",
        ),
    ]