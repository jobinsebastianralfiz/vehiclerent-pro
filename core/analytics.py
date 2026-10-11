"""Privacy-friendly page-view tracking for the admin Performance page.

Each public HTML page view becomes a PageView row. No IP address or cookie is stored: the visitor id is a hash of
IP + browser + date + SECRET_KEY, so it changes every day and can only be used to count unique visitors per day.
Bots, admin pages, assets and logged-in staff are skipped.
"""
import hashlib
from urllib.parse import urlparse

from django.conf import settings
from django.utils import timezone

SKIP_PREFIXES = ("/manage/", "/static/", "/media/", "/api/", "/enquiry/", "/robots.txt", "/sitemap.xml", "/llms.txt", "/favicon")
BOT_WORDS = ("bot", "crawl", "spider", "slurp", "preview", "fetch", "monitor", "lighthouse", "headless", "python-", "curl", "wget", "httpclient")
AI_HOSTS = ("chatgpt.com", "chat.openai.com", "openai.com", "perplexity.ai", "claude.ai", "gemini.google.com", "copilot.microsoft.com", "bard.google.com")


def classify_source(referrer, host, utm=""):
    """(source, referrer_host) from the Referer header and an optional utm_source."""
    utm = (utm or "").lower()
    ref = urlparse(referrer or "").netloc.lower().removeprefix("www.")
    probe = utm or ref
    if not probe:
        return "direct", ""
    if ref and ref == host.lower().removeprefix("www."):
        return "internal", ref
    for key, words in (("ai", AI_HOSTS + ("chatgpt", "perplexity", "claude", "gemini", "copilot")),
                       ("google", ("google.",)), ("bing", ("bing.", "duckduckgo")), ("whatsapp", ("whatsapp", "wa.me")),
                       ("facebook", ("facebook", "fb.", "m.me", "messenger")), ("instagram", ("instagram",)),
                       ("youtube", ("youtube", "youtu.be"))):
        if any(w in probe for w in words):
            return key, ref
    return "other", ref


def device_of(ua):
    ua = (ua or "").lower()
    if "ipad" in ua or "tablet" in ua or ("android" in ua and "mobile" not in ua):
        return "tablet"
    if "mobi" in ua or "iphone" in ua or "android" in ua:
        return "mobile"
    return "desktop"


def visitor_id(request):
    ip = (request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip() or request.META.get("REMOTE_ADDR", ""))
    raw = f"{ip}|{request.META.get('HTTP_USER_AGENT', '')}|{timezone.localdate()}|{settings.SECRET_KEY}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


class PageViewMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            self._record(request, response)
        except Exception:  # analytics must never break a page
            pass
        return response

    def _record(self, request, response):
        if request.method != "GET" or response.status_code != 200:
            return
        if not response.get("Content-Type", "").startswith("text/html"):
            return
        path = request.path
        if path.startswith(SKIP_PREFIXES):
            return
        if getattr(request, "user", None) is not None and request.user.is_authenticated:
            return  # the team's own visits would skew the numbers
        ua = request.META.get("HTTP_USER_AGENT", "")
        if not ua or any(w in ua.lower() for w in BOT_WORDS):
            return
        if request.META.get("HTTP_SEC_PURPOSE", "").startswith("prefetch") or request.META.get("HTTP_PURPOSE") == "prefetch":
            return
        from .models import PageView
        match = getattr(request, "resolver_match", None)
        slug = match.kwargs.get("slug", "") if match and match.url_name == "vehicle_detail" else ""
        source, ref = classify_source(request.META.get("HTTP_REFERER", ""), request.get_host(), request.GET.get("utm_source", ""))
        PageView.objects.create(path=path[:300], vehicle_slug=slug[:200], source=source, referrer_host=ref[:200],
                                device=device_of(ua), visitor=visitor_id(request))
