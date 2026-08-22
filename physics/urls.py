"""
URL configuration for physics project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from django.http import FileResponse
from django.contrib.sitemaps.views import sitemap
import os
from django.http import HttpResponse
from formulas.sitemap import sitemaps


def serve_sw(request):
    sw_path = os.path.join(settings.STATIC_ROOT, 'formulas/sw.js')
    return FileResponse(open(sw_path, 'rb'), content_type='application/javascript')

def serve_assetlinks(request):
    content = '''[{
  "relation": ["delegate_permission/common.handle_all_urls"],
  "target": {
    "namespace": "android_app",
    "package_name": "in.formulaverse.app",
    "sha256_cert_fingerprints": ["97:68:FF:24:F5:93:04:4B:5C:52:87:30:8F:42:4D:E0:47:0D:AB:1F:EB:4A:B1:99:D5:04:16:F4:E6:AC:BE:88"]
  }
}]'''
    return HttpResponse(content, content_type='application/json')

def ads_txt(request):
    content = "google.com, pub-2098916755752141, DIRECT, f08c47fec0942fa0"
    return HttpResponse(content, content_type="text/plain")

def robots_txt(request):
    content = """User-agent: *
Disallow: /api/
Disallow: /chatbot/
Disallow: /payment/
Disallow: /simple-login/
Disallow: /*/create-order/

Sitemap: https://formulaverse.in/sitemap.xml
"""
    return HttpResponse(content, content_type="text/plain")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('robots.txt', robots_txt),
    path('ads.txt', ads_txt),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('sw.js', serve_sw),
    path('.well-known/assetlinks.json', serve_assetlinks),
    path("", include("formulas.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

