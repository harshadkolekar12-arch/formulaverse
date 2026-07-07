from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


# Create your models here.

class Category(models.Model):
    name=models.CharField(max_length=100, null=True)
    explain=models.TextField(max_length=450, blank=True)
    simulation_url = models.URLField(blank = True, null = True)

    class Meta:
        verbose_name_plural="Categories"

    def __str__(self):
        return self.name

EXAM_CHOICES = [
    ('none', 'None'),
    ('jee', 'JEE'),
    ('neet', 'NEET'),
    ('both', 'JEE/NEET'),
    ]


class Formula(models.Model):
    title=models.CharField(max_length=80, null=True)
    form=models.CharField(null=True, max_length=100)
    chapter=models.CharField(max_length=50, null=True)
    description=models.CharField(max_length=200)
    given_by=models.CharField(blank=True, null=True, max_length=50, default='Derived')
    question=models.CharField(max_length=600)
    answer=models.CharField(max_length=100, null=True)
    form_info=models.CharField(max_length=200, null=True)
    category=models.ForeignKey(Category, on_delete=models.SET_NULL, related_name="fomulas", null=True)
    is_saved=models.BooleanField(default=False)
    session_key = models.CharField(max_length = 100, null = True, blank = True)
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    exam_tag = models.CharField(max_length = 10, choices=EXAM_CHOICES, default='none')

    def get_absolute_url(self):
        return reverse("single-formula-page", args=[self.id])

    def __str__(self):
        return f"{self.form} ({self.given_by})"


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







