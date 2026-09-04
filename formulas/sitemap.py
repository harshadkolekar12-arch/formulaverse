from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils.text import slugify
from .models import Formula, Chapter, PYQ, Article, Story

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['me', 'constants', 'pyq-papers', 'units-dimensions', 'privacy', 'terms']

    def location(self, item):
        return reverse(item)


class ChapterSitemap(Sitemap):
    priority = 0.9
    changefreq = 'monthly'

    def items(self):
        return Chapter.objects.all()

    def location(self, item):
        # Uses ID since Chapter model has no slug field
        return f'/chapter/{slugify(item.name)}/'


class FormulaSitemap(Sitemap):
    priority = 0.9
    changefreq = 'weekly'

    def items(self):
        return Formula.objects.all()

    def location(self, item):
        return f'/formula/{item.slug}/'


class StorySitemap(Sitemap):
    priority = 0.9
    changefreq = 'weekly'

    def items(self):
        return Story.objects.filter(is_published=True)

    def location(self, item):
        # Story maps to formula slug via its OneToOne relationship
        return f'/formula/{item.formula.slug}/story/'


class ArticleSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return Article.objects.filter(is_published=True)

    def location(self, item):
        # Explicit location to avoid 'get_absolute_url' AttributeError
        return f'/blog/{item.slug}/'


class PYQSitemap(Sitemap):
    priority = 0.7
    changefreq = 'monthly'

    def items(self):
        return PYQ.objects.all()

    def location(self, item):
        return f'/pyq/{item.id}/'


sitemaps = {
    'static': StaticViewSitemap,
    'chapters': ChapterSitemap,
    'formulas': FormulaSitemap,
    'stories': StorySitemap,
    'articles': ArticleSitemap,
    'pyqs': PYQSitemap,
}
