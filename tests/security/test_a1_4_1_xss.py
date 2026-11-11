"""A1 4.1 - Stored XSS and session hijacking (CWE-79, CWE-1004).
 
Before the fix, templates rendered user content with |safe, so a message
containing <script> ran in the victim's browser and could read the session
cookie. Now all user content is escaped and the cookie is HttpOnly.
"""
import uuid
 
from conftest import BASE, USER_IDS
 
PAYLOAD = "<script>alert('xss')</script>"
 
 
def test_session_cookie_is_httponly(anon):
    r = anon.post(f"{BASE}/login",
                  data={"email": "alice@student.uis.no", "password": "Alice123"},
                  allow_redirects=False)
    cookie = r.headers.get("set-cookie", "")
    assert "session_token=" in cookie
    assert "HttpOnly" in cookie
    assert "SameSite=lax" in cookie or "samesite=lax" in cookie.lower()
 
 
def test_script_in_message_is_escaped(as_user):
    marker = uuid.uuid4().hex[:8]
    alice, bob = as_user("alice"), as_user("bob")
    alice.post(f"{BASE}/messages",
               data={"recipient_id": USER_IDS["bob"], "content": f"{marker} {PAYLOAD}"})
 
    for page in ("/messages", "/dashboard"):
        r = bob.get(f"{BASE}{page}")
        assert PAYLOAD not in r.text, f"raw script rendered on {page}"
    # Legitimate behaviour: the message is still delivered, shown as plain text.
    r = bob.get(f"{BASE}/messages")
    assert marker in r.text
    assert "&lt;script&gt;" in r.text
 
 
def test_script_in_course_comment_is_escaped(as_user):
    marker = uuid.uuid4().hex[:8]
    alice = as_user("alice")
    alice.post(f"{BASE}/courses/1/comment", data={"content": f"{marker} {PAYLOAD}"})
    r = alice.get(f"{BASE}/courses/1")
    assert PAYLOAD not in r.text
    assert marker in r.text
 
 
def test_script_in_profile_bio_is_escaped(as_user):
    bob = as_user("bob")
    bob.post(f"{BASE}/profile/update",
             data={"full_name": "Bob Hansen", "bio": PAYLOAD})
    r = bob.get(f"{BASE}/profile")
    assert PAYLOAD not in r.text
    assert "&lt;script&gt;" in r.text
    bob.post(f"{BASE}/profile/update",
             data={"full_name": "Bob Hansen", "bio": "Likes backend development."})
 