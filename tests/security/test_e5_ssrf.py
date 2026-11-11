"""E5 - Server-Side Request Forgery in /resources/import (CWE-918).
 
Before the fix, the server fetched any URL, including internal services
(MailHog, the database, localhost) and file:// URLs, even without login.
Now: login is required, only http/https is allowed, and only hosts on an
allowlist can be fetched.
"""
import pytest
 
from conftest import BASE
 
BLOCKED_URLS = [
    "http://mailhog:8025/api/v2/messages",   # internal mailbox with reset tokens
    "http://db:5432",                         # internal database
    "http://localhost:8000/health",           # the backend itself
    "http://127.0.0.1:8000/health",
    "file:///etc/passwd",                     # local files
    "gopher://example.com",                   # other schemes
    "http://example.com@127.0.0.1/",          # userinfo trick
    "http://example.com.evil.test/",          # look-alike domain
]
 
 
def test_requires_login(anon):
    r = anon.get(f"{BASE}/resources/import", params={"url": "https://example.com"},
                 allow_redirects=False)
    assert r.status_code == 302
    assert r.headers["location"] == "/login"
 
 
@pytest.mark.parametrize("url", BLOCKED_URLS)
def test_internal_and_unsafe_urls_are_blocked(as_user, url):
    alice = as_user("alice")
    r = alice.get(f"{BASE}/resources/import", params={"url": url})
    assert r.status_code == 200
    assert "This URL is not allowed." in r.text
    assert "Response preview" not in r.text
 
 
def test_allowlisted_url_is_accepted(as_user):
    # Legitimate behaviour: an approved external resource is not blocked.
    alice = as_user("alice")
    r = alice.get(f"{BASE}/resources/import", params={"url": "https://example.com"})
    assert r.status_code == 200
    assert "This URL is not allowed." not in r.text
 
 
def test_errors_do_not_leak_details(as_user):
    # An allowlisted host on a closed port fails, but the error is generic.
    alice = as_user("alice")
    r = alice.get(f"{BASE}/resources/import", params={"url": "http://example.com:1/"})
    assert "This URL is not allowed." not in r.text
    assert "Connection" not in r.text
    assert "Errno" not in r.text
 