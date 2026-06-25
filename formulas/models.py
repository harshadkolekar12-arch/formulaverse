from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


# Create your models here.

class Category(models.Model):
    name=models.CharField(max_length=100, null=True)
    explain=models.TextField(max_length=350, blank=True)

    class Meta:
        verbose_name_plural="Categories"

    def __str__(self):
        return self.name

class Formula(models.Model):
    title=models.CharField(max_length=80, null=True)
    form=models.CharField(null=True, max_length=100)
    chapter=models.CharField(max_length=50, null=True)
    description=models.CharField(max_length=200)
    given_by=models.CharField(blank=True, null=True, max_length=50, default='Unknown')
    question=models.CharField(max_length=600)
    answer=models.CharField(max_length=50, null=True)
    solve=models.CharField(blank=True, null=True, max_length=200)
    correct_answer=models.CharField(null=True, blank=True, max_length=500)
    explanation=models.ImageField(upload_to="posts", blank=True, null=True)
    form_info=models.CharField(max_length=200, null=True)
    category=models.ForeignKey(Category, on_delete=models.SET_NULL, related_name="fomulas", null=True)
    is_saved=models.BooleanField(default=False)
    session_key = models.CharField(max_length = 100, null = True, blank = True)
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    video_url = models.URLField(blank = True, null = True)










    def get_absolute_url(self):
        return reverse("single-formula-page", args=[self.id])

    def __str__(self):
        return f"{self.form} ({self.given_by})"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    profile_pic = models.ImageField(
        upload_to = 'profile_pics/',
        blank = True,
        null =True
        )

    def __str__(self):
        return f"{self.user.username}'s Profile"
