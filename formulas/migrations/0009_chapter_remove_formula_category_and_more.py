import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("formulas", "0008_alter_formula_answer"),
    ]

    operations = [
        migrations.CreateModel(
            name="Chapter",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, null=True)),
                ("explain", models.TextField(blank=True, max_length=450)),
                ("simulation_url", models.URLField(blank=True, null=True)),
            ],
            options={
                "verbose_name_plural": "Chapters",
            },
        ),
        migrations.RemoveField(
            model_name="formula",
            name="category",
        ),
        migrations.RemoveField(
            model_name="formula",
            name="form_info",
        ),
        migrations.RemoveField(
            model_name="formula",
            name="question",
        ),
        migrations.AddField(
            model_name="formula",
            name="example",
            field=models.TextField(blank=True, max_length=600, null=True),
        ),
        migrations.AddField(
            model_name="formula",
            name="units",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="formula",
            name="variables",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="formula",
            name="when_to_use",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name="formula",
            name="answer",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="formula",
            name="description",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name="formula",
            name="form",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name="formula",
            name="given_by",
            field=models.CharField(blank=True, default="Derived", max_length=50),
        ),
        migrations.AlterField(
            model_name="formula",
            name="title",
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
    ]