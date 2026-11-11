"""
    E3- Insecure configuration (CWE-209 / CWE-489).
    
    Before the fix, /error showed the full Python traceback to the user.
    Now the user only sees a generic message and the details go to the server log.
"""
    
from conftest import BASE


def test_error_page_does_not_leak_traceback(anon):
    r = anon.get(f"{BASE}/error")
    assert r.status_code == 500
    assert "Traceback" not in r.text
    assert "ZeroDivisionError" not in r.text
    assert 'File "' not in r.text
    
    
def test_error_page_shows_generic_message(anon):
    r = anon.get(f"{BASE}/error")
    assert "Something went wrong" in r.text
    
    
def test_app_still_healthy(anon):
    r = anon.get(f"{BASE}/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}