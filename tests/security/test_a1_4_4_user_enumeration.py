"""A1 4.4 - User enumeration on login and password reset (CWE-204).
 
Before the fix, the login said "No account found" for unknown emails and
"Invalid password" for known ones, and password reset said "No user found".
Now both cases give exactly the same answer.
"""
import uuid
 
from conftest import BASE
 
GENERIC_LOGIN = "Invalid email or password."
 
 
def login_response(session, email, password):
    return session.post(f"{BASE}/login", data={"email": email, "password": password},
                        allow_redirects=False)
 
 
def test_login_same_answer_for_unknown_email_and_wrong_password(anon):
    unknown = login_response(anon, "nobody@student.uis.no", "whatever")
    wrong = login_response(anon, "alice@student.uis.no", "whatever")
    assert unknown.status_code == wrong.status_code == 200
    assert GENERIC_LOGIN in unknown.text
    assert GENERIC_LOGIN in wrong.text
    assert "No account found" not in unknown.text
    assert unknown.text == wrong.text
 
 
def test_reset_password_same_answer(anon):
    known = anon.post(f"{BASE}/reset-password", data={"email": "alice@student.uis.no"})
    unknown = anon.post(f"{BASE}/reset-password", data={"email": "nobody@student.uis.no"})
    assert known.status_code == unknown.status_code == 200
    assert "No user found" not in unknown.text
    assert known.text == unknown.text
 
 
def test_correct_login_still_works(anon):
    # Legitimate behaviour: valid credentials still log in.
    r = login_response(anon, "alice@student.uis.no", "Alice123")
    assert r.status_code == 302
    assert r.headers["location"] == "/dashboard"
 
 
def test_register_same_answer_for_existing_email(anon):
    existing = anon.post(f"{BASE}/register", allow_redirects=False,
                         data={"email": "alice@student.uis.no", "full_name": "X", "password": "Whatever1"})
    new = anon.post(f"{BASE}/register", allow_redirects=False,
                    data={"email": f"user-{uuid.uuid4().hex[:8]}@uis.no", "full_name": "X", "password": "Whatever1"})
    assert existing.status_code == new.status_code == 302
    assert existing.headers["location"] == new.headers["location"] == "/login"
    assert "already exists" not in existing.text
 