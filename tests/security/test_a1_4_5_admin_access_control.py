"""A1 4.5 - Missing access control on /admin/* (CWE-862, CWE-639).
 
Before the fix, only /admin checked the role. Other admin pages were open to
any logged-in user, the role change trusted an "x-role" header, and the grade
update trusted a "role" form field. Now every admin route checks the role
stored in the session.
"""
import re
import pytest
 
from conftest import BASE, USER_IDS
 
ADMIN_PAGES = ["/admin", "/admin/users", "/admin/grades", "/admin/search-users?q=a"]
 
 
def role_of(admin_session, email):
    """Read a user's current role from the admin user search page."""
    r = admin_session.get(f"{BASE}/admin/search-users", params={"q": email})
    m = re.search(re.escape(email) + r'</td><td><span class="badge[^"]*">(\w+)</span>', r.text)
    return m.group(1) if m else None
 
 
@pytest.mark.parametrize("page", ADMIN_PAGES)
def test_student_is_redirected_from_admin_pages(as_user, page):
    alice = as_user("alice")
    r = alice.get(f"{BASE}{page}", allow_redirects=False)
    assert r.status_code == 302
    assert r.headers["location"] == "/dashboard"
 
 
@pytest.mark.parametrize("page", ADMIN_PAGES)
def test_anonymous_is_redirected_to_login(anon, page):
    r = anon.get(f"{BASE}{page}", allow_redirects=False)
    assert r.status_code == 302
    assert r.headers["location"] == "/login"
 
 
def test_student_cannot_change_roles_even_with_x_role_header(as_user):
    alice, admin = as_user("alice"), as_user("admin")
    r = alice.post(f"{BASE}/admin/users/{USER_IDS['alice']}/role",
                   data={"role": "admin"}, headers={"x-role": "admin"},
                   allow_redirects=False)
    assert r.status_code == 302
    assert r.headers["location"] == "/dashboard"
    assert role_of(admin, "alice@student.uis.no") == "student"
 
 
def test_student_cannot_change_grades(as_user):
    alice, teacher = as_user("alice"), as_user("teacher")
    alice.post(f"{BASE}/admin/grades/1/update",
               data={"grade_value": "A+", "feedback": "hacked", "role": "teacher"})
    r = teacher.get(f"{BASE}/admin/grades")
    assert "hacked" not in r.text
 
 
def test_admin_can_still_manage_roles(as_user):
    # Legitimate behaviour: an admin can still change a role (and change it back).
    admin = as_user("admin")
    admin.post(f"{BASE}/admin/users/{USER_IDS['charlie']}/role", data={"role": "ta"})
    assert role_of(admin, "charlie@student.uis.no") == "ta"
    admin.post(f"{BASE}/admin/users/{USER_IDS['charlie']}/role", data={"role": "student"})
    assert role_of(admin, "charlie@student.uis.no") == "student"
 
 
def test_teacher_can_still_update_grades(as_user):
    teacher = as_user("teacher")
    teacher.post(f"{BASE}/admin/grades/1/update",
                 data={"grade_value": "B+", "feedback": "Good structure, include more trace evidence."})
    r = teacher.get(f"{BASE}/admin/grades")
    assert "Good structure, include more trace evidence." in r.text
 
 
def test_teacher_cannot_make_self_admin(as_user):
    teacher, admin = as_user("teacher"), as_user("admin")
    teacher.post(f"{BASE}/admin/users/{USER_IDS['teacher']}/role", data={"role": "admin"})
    assert role_of(admin, "teacher@dat250.local") == "teacher"
 
 
def test_teacher_cannot_change_admin_role(as_user):
    teacher, admin = as_user("teacher"), as_user("admin")
    teacher.post(f"{BASE}/admin/users/{USER_IDS['admin']}/role", data={"role": "student"})
    assert role_of(admin, "admin@dat250.local") == "admin"
 
 
def test_teacher_can_still_manage_student_roles(as_user):
    teacher, admin = as_user("teacher"), as_user("admin")
    teacher.post(f"{BASE}/admin/users/{USER_IDS['charlie']}/role", data={"role": "ta"})
    assert role_of(admin, "charlie@student.uis.no") == "ta"
    teacher.post(f"{BASE}/admin/users/{USER_IDS['charlie']}/role", data={"role": "student"})
    assert role_of(admin, "charlie@student.uis.no") == "student"
 