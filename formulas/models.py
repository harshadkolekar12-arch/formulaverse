from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
import uuid
from django.core.validators import FileExtensionValidator


# Create your models here.

class Chapter(models.Model):
    name=models.CharField(max_length=100, null=True)
    explain=models.TextField(max_length=450, blank=True)
    simulation_url = models.URLField(blank = True, null = True)
    sim_video=models.URLField(null=True, blank=True)
    sim_thumbnail=models.ImageField(upload_to="sim_video/thumbnail/", null=True, blank=True)
    is_premium = models.BooleanField(default=False)
    price_inr = models.PositiveIntegerField(default=49)  # ₹, editable per chapter

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
    given_by = models.CharField(max_length=300, blank=True, default='Derived')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    exam_tag = models.CharField(max_length=10, choices=EXAM_CHOICES, default='none')
    derivation_image = models.FileField(
        upload_to='derivation/', null=True, blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'png', 'jpg', 'jpeg'])]
    )
    mnemonic=models.TextField(blank=True, null=True)
    worked_example=models.TextField(blank=True, null=True)
    example = models.TextField(blank=True, null=True)
    answer = models.CharField(max_length=500, blank=True, null=True)
    common_mistakes=models.TextField(blank=True, null=True)
    desmos_graph_id=models.CharField(max_length=200, null=True, blank=True)
    diagram_url=models.FileField(
        upload_to='diagram/', null=True, blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'png', 'jpg', 'jpeg', 'svg'])]
        )


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



class SimpleUser(models.Model):
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=100, null=True, blank=True)
    date_of_birth = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"User (Name: {self.name}) - {self.created_at.strftime('%d %b %Y')}"

    class Meta:
        ordering = ['-created_at']



class PurchasedChapter(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name="purchases")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=100, null=True, blank=True)

    razorpay_order_id = models.CharField(max_length=100)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    amount_inr = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=[("created", "Created"), ("paid", "Paid"), ("failed", "Failed")],
        default="created",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["session_key", "chapter"]),
            models.Index(fields=["user", "chapter"]),
        ]

    def _str_(self):
        return f"{self.chapter.name} — {self.status} — {self.razorpay_order_id}"


def has_purchased(chapter, request):
    qs = PurchasedChapter.objects.filter(chapter=chapter, status="paid")
    if request.user.is_authenticated:
        if qs.filter(user=request.user).exists():
            return True
    session_key = request.session.session_key
    if session_key and qs.filter(session_key=session_key).exists():
        return True
    return False


class SavedFormula(models.Model):
    user = models.ForeignKey(SimpleUser, on_delete=models.CASCADE, related_name='saved_formulas')
    formula = models.ForeignKey(Formula, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'formula')  # prevents duplicate saves


class ExamDate(models.Model):
    EXAM_CHOICES = [
        ('jee_main_1', 'JEE Main Session 1'),
        ('jee_main_2', 'JEE Main Session 2'),
        ('jee_advanced', 'JEE Advanced'),
        ('neet', 'NEET'),
    ]
    exam_key = models.CharField(max_length=20, choices=EXAM_CHOICES)
    display_name = models.CharField(max_length=100)
    exam_date = models.DateField()

    def __str__(self):
        return f"{self.display_name} — {self.exam_date}"

    class Meta:
        ordering = ['exam_date']
