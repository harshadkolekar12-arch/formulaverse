from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Formula

class FormulaSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Formula.objects.all()

    def location(self, obj):
        return reverse('single-formula-page', args=[obj.pk])

class StaticSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.8

    def items(self):
        return ['index-page', 'base-page']

    def location(self, item):
        return reverse(item)