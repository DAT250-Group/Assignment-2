"""E6 - Predictable password reset token (CWE-330, CWE-640).
 
Before the fix, the reset token was the last six digits of the current time,
it never expired, it could be reused and it was printed to the server log.
Now it is a random 32-byte token that expires after 30 minutes and can only
be used once.
 
These tests read the database directly on 127.0.0.1:5432 (see test_e4).
"""
import os
 
import psycopg2
 
from conftest import BASE
 
DB_URL = os.getenv("TEST_DATABASE_URL", "postgresql://dat250:dat250@127.0.0.1:5432/dat250")
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
    session.post(f"{BASE}/reset-password", data={"email": email})
    row = db(
        """SELECT t.token FROM password_reset_tokens t JOIN users u ON u.id = t.user_id
           WHERE u.email=%s ORDER BY t.id DESC LIMIT 1""",
        (email,), fetch=True,
    )
    return row[0]
 
 
def set_password(session, token, password):
    return session.post(f"{BASE}/reset-password/{token}",
                        data={"new_password": password}, allow_redirects=False)
 
 
def test_token_is_long_and_random(anon):
    first = new_token_for(anon, BOB)
    second = new_token_for(anon, BOB)
    assert len(first) >= 40
    assert not first.isdigit()
    assert first != second
 
 
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
       (token,))
    r = set_password(anon, token, "Hacked123")
    assert "Invalid or expired token" in r.text
 
 
def test_guessed_token_is_rejected(anon):
    r = set_password(anon, "123456", "Hacked123")
    assert "Invalid or expired token" in r.text
 
 
def test_bob_can_still_log_in(anon):
    r = anon.post(f"{BASE}/login", data={"email": BOB, "password": "Bob123"}, allow_redirects=False)
    assert r.status_code == 302
 