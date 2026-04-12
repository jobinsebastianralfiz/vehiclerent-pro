from django.shortcuts import redirect
from django.conf import settings


class AdminLoginRequiredMiddleware:
    EXEMPT_URLS = ["/manage/login/"]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/manage/") and request.path not in self.EXEMPT_URLS:
            if not request.user.is_authenticated:
                return redirect(f"{settings.LOGIN_URL}?next={request.path}")
        return self.get_response(request)
