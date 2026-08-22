from django.http import HttpResponsePermanentRedirect

class DomainRedirectMiddleware:
    def _init_(self, get_response):
        self.get_response = get_response

    def _call_(self, request):
        host = request.get_host().split(':')[0]
        if 'pythonanywhere.com' in host:
            target_url = f"https://formulaverse.in{request.path}"
            return HttpResponsePermanentRedirect(target_url)

        return  self.get_response(request)