"""Spam checks for public forms: a honeypot field, a signed render timestamp
(bots post instantly or replay stale pages), and a few content signals.

Templates add the fields with {% include "public/includes/_antispam.html" %};
views call check(request) and treat a non-empty result as spam.
"""
import json
import logging
import re
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.core import signing

logger = logging.getLogger(__name__)

HONEYPOT_FIELD = "website"
TOKEN_FIELD = "form_ts"
MIN_SECONDS = 3            # a human can't fill the form faster than this
MAX_AGE = 60 * 60 * 24 * 2  # pages left open for two days still work

_SALT = "core.antispam"
_URL = re.compile(r"(https?://|www\.|\[url|<a\s)", re.I)


def make_token():
    return signing.dumps(int(time.time()), salt=_SALT)


def check(request):
    """Return a short reason string if the POST looks like spam, else ''."""
    if request.POST.get(HONEYPOT_FIELD, "").strip():
        return "honeypot"
    try:
        issued = signing.loads(request.POST.get(TOKEN_FIELD, ""), salt=_SALT, max_age=MAX_AGE)
    except signing.BadSignature:
        return "token"
    if time.time() - int(issued) < MIN_SECONDS:
        return "too_fast"
    if _URL.search(request.POST.get("name", "")):
        return "link_in_name"
    if len(_URL.findall(request.POST.get("message", ""))) > 1:
        return "links_in_message"
    return ""


TURNSTILE_VERIFY = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


def turnstile_ok(request):
    """Cloudflare Turnstile check. Always passes while TURNSTILE_SECRET_KEY isn't set.
    Call it only for an otherwise valid form: each token can be verified once."""
    secret = settings.TURNSTILE_SECRET_KEY
    if not secret:
        return True
    token = request.POST.get("cf-turnstile-response", "")
    if not token:
        return False
    data = urlencode({"secret": secret, "response": token, "remoteip": client_ip(None, request)}).encode()
    try:
        with urlopen(Request(TURNSTILE_VERIFY, data=data), timeout=6) as resp:
            return bool(json.load(resp).get("success"))
    except Exception:
        # Cloudflare unreachable: let it through rather than lose a real customer's enquiry
        logger.warning("Turnstile verification failed to run", exc_info=True)
        return True


def client_ip(group, request):
    """Rate-limit key. REMOTE_ADDR is the visitor on Namecheap/LiteSpeed."""
    return request.META.get("REMOTE_ADDR", "")
