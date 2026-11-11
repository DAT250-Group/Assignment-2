"""E4 - Weak password hashing (CWE-916).
 
Before the fix, passwords were stored as unsalted SHA-256 hashes.
Now they are stored with bcrypt (random salt, cost factor 12).
 
These tests read the database directly. It is reachable from the host
on 127.0.0.1:5432 (see docker-compose.yml).
"""
import os
import uuid
 
import psycopg2
import pytest
 
from conftest import BASE, ACCOUNTS
 
DB_URL = os.getenv("TEST_DATABASE_URL", "postgresql://dat250:dat250@127.0.0.1:5432/dat250")
 
 
def stored_hash(email):
    conn = psycopg2.connect(DB_URL)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT password_hash FROM users WHERE email=%s", (email,))
            row = cur.fetchone()
            return row[0] if row else None
    finally:
        conn.close()
 
 
def register(session, email, password):
    return session.post(
        f"{BASE}/register",
        data={"email": email, "full_name": "Test User", "password": password},
        allow_redirects=False,
    )
 
 
@pytest.mark.parametrize("name", ACCOUNTS.keys())
def test_seed_users_use_bcrypt(name):
    email, _ = ACCOUNTS[name]
    h = stored_hash(email)
    assert h.startswith("$2b$12$"), f"{email} is not stored with bcrypt: {h[:10]}..."
 
 
def test_new_user_is_stored_with_bcrypt_and_can_log_in(anon):
    email = f"test-{uuid.uuid4().hex[:8]}@student.uis.no"
    r = register(anon, email, "Secret123!")
    assert r.status_code == 302
 
    h = stored_hash(email)
    assert h.startswith("$2b$12$")
    assert "Secret123!" not in h
 
    # Legitimate behaviour: the new user can log in with the right password.
    r = anon.post(f"{BASE}/login", data={"email": email, "password": "Secret123!"},
                  allow_redirects=False)
    assert r.status_code == 302
 
 
def test_same_password_gives_different_hashes(anon):
    # The random salt means two users with the same password get different hashes.
    a = f"salt-a-{uuid.uuid4().hex[:8]}@student.uis.no"
    b = f"salt-b-{uuid.uuid4().hex[:8]}@student.uis.no"
    register(anon, a, "SamePassword1")
    register(anon, b, "SamePassword1")
    assert stored_hash(a) != stored_hash(b)
 
 
def test_wrong_password_is_rejected(anon):
    r = anon.post(f"{BASE}/login",
                  data={"email": "alice@student.uis.no", "password": "Admin123"},
                  allow_redirects=False)
    assert r.status_code == 200
    assert "Invalid email or password." in r.text
 