import os
import pytest
import requests

BASE = os.getenv("BASE_URL", "http://localhost:18181")
ACCOUNTS = {
    "admin": ("admin@dat250.local", "Admin123"),
    "teacher": ("teacher@dat250.local", "Teacher123"),
    "ta": ("ta@dat250.local", "TA123"),
    "alice": ("alice@student.uis.no", "Alice123"),
    "bob": ("bob@student.uis.no", "Bob123"),
}

USER_IDS = {"admin": 1, "teacher": 2, "ta": 3, "alice": 4, "bob": 5, "charlie": 6}

def login(name):
    email, password = ACCOUNTS[name]
    session = requests.Session()
    r = session.post(f"{BASE}/login", data={"email": email, "password": password},
                     allow_redirects=False)
    assert r.status_code == 302, f"Login failed for {name}: {r.status_code} {r.text}"
    return session

@pytest.fixture(scope="session", autouse=True)
def app_is_running():
    try:
        requests.get(f"{BASE}/health", timeout=5)
    except requests.ConnectionError:
        pytest.exit(f"Cannot connect to the application at {BASE}. Make sure it is running.", returncode=1)
        
@pytest.fixture
def as_user():
    return login

@pytest.fixture
def anon():
    return requests.Session()