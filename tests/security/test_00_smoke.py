import pytest

from conftest import ACCOUNTS, BASE

@pytest.mark.parametrize("name", ACCOUNTS.keys())
def test_every_test_account_can_log_in(as_user, name):
    as_user(name)
    
def test_logged_in_student_sees_dashboard(as_user):
    alice = as_user("alice")
    r = alice.get(f"{BASE}/dashboard")
    assert r.status_code == 200
    assert "Alice Nilsen" in r.text