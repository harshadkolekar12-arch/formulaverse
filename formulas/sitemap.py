from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Formula, Chapter, PYQ, DailyChallenge

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        # List all main static view names here
        return ['me', 'constants', 'pyq-papers', 'units-dimensions', 'privacy', 'terms']

    def location(self, item):
        return reverse(item)

class ChapterSitemap(Sitemap):
    priority = 0.9
    changefreq = 'monthly'

    def items(self):
        return Chapter.objects.all()

class FormulaSitemap(Sitemap):
    priority = 0.9
    changefreq = 'weekly'

    def items(self):
        return Formula.objects.all()

    def location(self, item):
        return f'/formula/{item.slug}/'

class PYQSitemap(Sitemap):
    priority = 0.7
    changefreq = 'monthly'

    def items(self):
        return PYQ.objects.all()

class DailyChallengeSitemap(Sitemap):
    priority = 0.6
    changefreq = 'daily'

    def items(self):
        return DailyChallenge.objects.all()

# Master sitemaps dictionary
sitemaps = {
    'static': StaticViewSitemap,
    'chapters': ChapterSitemap,
    'formulas': FormulaSitemap,
    'pyqs': PYQSitemap,
    'daily_challenges': DailyChallengeSitemap,
}