from django.http import HttpResponsePermanentRedirect

class DomainRedirectMiddleware:
    def _init_(self, get_response):
        self.get_response = get_response

    def _call_(self, request):
        host = request.get_host().split(':')[0]
        if 'pythonanywhere.com' in host:
            return HttpResponsePermanentRedirect(
                'https://formulaverse.in' + request.get_full_path()
            )
        response = self.get_response(request)
        return response