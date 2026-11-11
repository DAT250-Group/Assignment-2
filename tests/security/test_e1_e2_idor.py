"""E1/E2 - Insecure Direct Object References (CWE-639).
 
Before the fix, changing the id in /grades/{id}, /messages/{id} or
/profile/{id} showed other users' private data. Now the owner is checked.
"""
from conftest import BASE, USER_IDS
 
# From db/seed.sql: grade 1 belongs to Alice, grade 2 to Bob.
# Message 1 was sent by the teacher to Alice.
 
 
def test_student_sees_own_grade(as_user):
    r = as_user("alice").get(f"{BASE}/grades/1")
    assert r.status_code == 200
    assert "Alice Nilsen" in r.text
    assert "B+" in r.text
 
 
def test_student_cannot_see_other_students_grade(as_user):
    r = as_user("alice").get(f"{BASE}/grades/2")
    assert "Bob Hansen" not in r.text
 
 
def test_recipient_sees_own_message(as_user):
    r = as_user("alice").get(f"{BASE}/messages/1")
    assert "Please remember to include screenshots" in r.text
 
 
def test_other_user_cannot_read_message(as_user):
    r = as_user("bob").get(f"{BASE}/messages/1")
    assert "Please remember to include screenshots" not in r.text
 
 
def test_student_cannot_open_other_profile(as_user):
    r = as_user("alice").get(f"{BASE}/profile/{USER_IDS['bob']}", allow_redirects=False)
    assert r.status_code == 302
    assert r.headers["location"] == "/profile"
 
 
def test_admin_can_still_open_any_profile(as_user):
    r = as_user("admin").get(f"{BASE}/profile/{USER_IDS['bob']}")
    assert r.status_code == 200
    assert "Bob Hansen" in r.text
 