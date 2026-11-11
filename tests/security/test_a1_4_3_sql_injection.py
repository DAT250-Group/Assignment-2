"""A1 4.3 - SQL injection in the search features (CWE-89).
 
Before the fix, /admin/search-users and /courses/search built SQL with
f-strings, so input like ' OR '1'='1 changed the query. Now both use
parameterized queries.
"""
from conftest import BASE
 
INJECTIONS = [
    "' OR '1'='1",
    "%' OR 1=1 --",
    "' UNION SELECT 1,email,password_hash,role FROM users --",
    "'",
]
 
 
def test_user_search_injection_returns_nothing(as_user):
    admin = as_user("admin")
    for payload in INJECTIONS:
        r = admin.get(f"{BASE}/admin/search-users", params={"q": payload})
        assert r.status_code == 200, f"server error for {payload!r}"
        assert "alice@student.uis.no" not in r.text, f"injection worked: {payload!r}"
        assert "$2b$" not in r.text
 
 
def test_user_search_still_works(as_user):
    # Legitimate behaviour: a normal search finds the right user.
    admin = as_user("admin")
    r = admin.get(f"{BASE}/admin/search-users", params={"q": "alice"})
    assert "alice@student.uis.no" in r.text
    assert "bob@student.uis.no" not in r.text
 
 
def test_course_search_injection_returns_nothing(as_user):
    alice = as_user("alice")
    for payload in INJECTIONS:
        r = alice.get(f"{BASE}/courses/search", params={"q": payload})
        assert r.status_code == 200, f"server error for {payload!r}"
        assert "DAT220" not in r.text, f"injection worked: {payload!r}"
        assert "$2b$" not in r.text
 
 
def test_course_search_still_works(as_user):
    alice = as_user("alice")
    r = alice.get(f"{BASE}/courses/search", params={"q": "Database"})
    assert "DAT220" in r.text
 