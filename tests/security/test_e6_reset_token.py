"""E6 - Predictable password reset token (CWE-330, CWE-640).

Before the fix, the reset token was the last six digits of the current time,
it never expired, it could be reused and it was printed to the server log.
Now it is a random 32-byte token that expires after 30 minutes and can only
be used once. Only a SHA-256 hash of the token is stored in the database,
and asking for a new reset link cancels the previous one.

These tests read the database directly on 127.0.0.1:5432 (see test_e4) and
the reset e-mails from the MailHog API on 127.0.0.1:8025.
"""
import hashlib
import os
import re

import psycopg2
import requests

from conftest import BASE

DB_URL = os.getenv("TEST_DATABASE_URL", "postgresql://dat250:dat250@127.0.0.1:5432/dat250")
MAILHOG_API = os.getenv("TEST_MAILHOG_API", "http://127.0.0.1:8025")
BOB = "bob@student.uis.no"


def db(sql, params=(), fetch=False):
    conn = psycopg2.connect(DB_URL)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            row = cur.fetchone() if fetch else None
        conn.commit()
        return row
    finally:
        conn.close()


def new_token_for(session, email):
    """Ask for a reset link and read the token from the e-mail, like the user would."""
    session.post(f"{BASE}/reset-password", data={"email": email})
    r = requests.get(f"{MAILHOG_API}/api/v2/search",
                     params={"kind": "to", "query": email, "limit": 1}, timeout=5)
    body = r.json()["items"][0]["Content"]["Body"]
    return re.search(r"/reset-password/([A-Za-z0-9_-]+)", body).group(1)


def sha256(token):
    return hashlib.sha256(token.encode()).hexdigest()


def set_password(session, token, password):
    return session.post(f"{BASE}/reset-password/{token}",
                        data={"new_password": password}, allow_redirects=False)


def test_token_is_long_and_random(anon):
    first = new_token_for(anon, BOB)
    second = new_token_for(anon, BOB)
    assert len(first) >= 40
    assert not first.isdigit()
    assert first != second


def test_only_a_hash_of_the_token_is_stored(anon):
    token = new_token_for(anon, BOB)
    assert db("SELECT 1 FROM password_reset_tokens WHERE token=%s", (token,), fetch=True) is None
    assert db("SELECT 1 FROM password_reset_tokens WHERE token=%s", (sha256(token),), fetch=True)


def test_new_request_cancels_the_old_token(anon):
    old = new_token_for(anon, BOB)
    new_token_for(anon, BOB)
    r = set_password(anon, old, "Hacked123")
    assert "Invalid or expired token" in r.text


def test_token_works_once_and_then_is_rejected(anon):
    token = new_token_for(anon, BOB)
    r = set_password(anon, token, "Bob123")          # legitimate use, same password
    assert r.status_code == 302
    assert r.headers["location"] == "/login"
    again = set_password(anon, token, "Hacked123")
    assert "Invalid or expired token" in again.text


def test_expired_token_is_rejected(anon):
    token = new_token_for(anon, BOB)
    db("UPDATE password_reset_tokens SET created_at = created_at - INTERVAL '31 minutes' WHERE token=%s",
       (sha256(token),))
    r = set_password(anon, token, "Hacked123")
    assert "Invalid or expired token" in r.text


def test_guessed_token_is_rejected(anon):
    r = set_password(anon, "123456", "Hacked123")
    assert "Invalid or expired token" in r.text


def test_bob_can_still_log_in(anon):
    r = anon.post(f"{BASE}/login", data={"email": BOB, "password": "Bob123"}, allow_redirects=False)
    assert r.status_code == 302