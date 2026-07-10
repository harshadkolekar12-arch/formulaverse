from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


# Create your models here.

class Chapter(models.Model):
    name=models.CharField(max_length=100, null=True)
    explain=models.TextField(max_length=450, blank=True)
    simulation_url = models.URLField(blank = True, null = True)

    class Meta:
        verbose_name_plural="Chapters"

    def __str__(self):
        return self.name

EXAM_CHOICES = [
    ('none', 'None'),
    ('jee', 'JEE'),
    ('neet', 'NEET'),
    ('both', 'JEE/NEET'),
    ]


class Formula(models.Model):
    # --- Essential ---
    title = models.CharField(max_length=80, blank=True, null=True)
    form = models.CharField(max_length=150, blank=True, null=True)  # renamed from 'form' for clarity
    variables = models.CharField(max_length=200, blank=True, null=True)  # e.g. "E = Energy, m = Mass, c = Speed of light"
    chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, max_length=50, blank=True, null=True)  # single source of truth, replaces category+chapter split
    description = models.CharField(max_length=200, blank=True, null=True)
    units = models.CharField(max_length=100, blank=True, null=True)  # e.g. "E: Joules, m: kg, c: m/s"
    when_to_use = models.CharField(max_length=200, blank=True, null=True)  # e.g. "Use when converting rest mass to energy"
    example = models.TextField(max_length=600, blank=True, null=True)
    answer = models.CharField(max_length=100, blank=True, null=True)
    given_by = models.CharField(max_length=100, blank=True, default='Derived')
    is_saved = models.BooleanField(default=False)
    session_key = models.CharField(max_length=100, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    exam_tag = models.CharField(max_length=10, choices=EXAM_CHOICES, default='none')

    def get_absolute_url(self):
        return reverse("single-formula-page", args=[self.id])

    def _str_(self):
        return f"{self.title} ({self.given_by})"




class PYQ(models.Model):
    EXAM_CHOICES = [
        ('JEE', 'JEE'),
        ('NEET', 'NEET'),
        ('BOTH', 'JEE/NEET'),
        ]

    category = models.CharField(max_length = 100)
    year = models.PositiveIntegerField()
    exam = models.CharField(max_length = 10, choices = EXAM_CHOICES, default = 'JEE')
    formula_name = models.CharField(max_length = 150)
    formula_exp = models.CharField(max_length = 200)
    times_asked = models.PositiveIntegerField(default = 1)



    class Meta:
        ordering = ['-year']

    def __str__(self):
        return f"{self.formula_name} ({self.category}, {self.year})"







