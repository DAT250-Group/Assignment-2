"""A1 4.2 - Privilege escalation through the profile form (CWE-915).
 
Before the fix, /profile/update accepted a hidden "role" field and saved it,
so a student could make themselves admin. Now the role is never taken from
the profile form.
"""
import re
 
from conftest import BASE
 
 
def role_of(admin_session, email):
    """Read a user's current role from the admin user search page."""
    r = admin_session.get(f"{BASE}/admin/search-users", params={"q": email})
    m = re.search(re.escape(email) + r'</td><td><span class="badge[^"]*">(\w+)</span>', r.text)
    return m.group(1) if m else None
 
 
def test_student_cannot_set_own_role(as_user):
    bob, admin = as_user("bob"), as_user("admin")
    bob.post(f"{BASE}/profile/update",
             data={"full_name": "Bob Hansen", "role": "admin"})
    assert role_of(admin, "bob@student.uis.no") == "student"
 
    r = bob.get(f"{BASE}/admin/users", allow_redirects=False)
    assert r.status_code == 302
 
 
def test_profile_update_still_works(as_user):
    # Legitimate behaviour: the allowed fields are still saved.
    bob = as_user("bob")
    bob.post(f"{BASE}/profile/update",
             data={"full_name": "Bob Hansen", "phone": "+47 12345678"})
    r = bob.get(f"{BASE}/profile")
    assert "+47 12345678" in r.text
    bob.post(f"{BASE}/profile/update",
             data={"full_name": "Bob Hansen", "phone": "+47 40001005",
                       "address": "Sandnes", "bio": "Likes backend development."})
 