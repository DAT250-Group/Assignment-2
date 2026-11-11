# DAT250 SecureApp — UiS Student Project Portal

## 1. Purpose
This repository contains a local-only lab web application for DAT250 Information and Software Security. It is designed for safe classroom use on your own machine.

## 2. Required tools
- Docker Desktop
- Git
- A web browser
- VS Code (optional)

## 3. Quick start
```bash
git clone https://github.com/DAT250-Group/Assignment-2.git
cd Assignment-2

# Create your local environment file (it is not committed to Git)
cp .env.example .env          # Windows PowerShell: copy .env.example .env
# Then edit .env and set SESSION_SECRET to a long random value, for example:
#   python -c "import secrets; print(secrets.token_hex(32))"

docker compose down -v
docker compose up --build
```

> The application refuses to start if `SESSION_SECRET` is missing. This is intentional (see "Security fixes" below).

## 4. URLs
- App: [http://localhost:18181](http://localhost:18181)
- MailHog inbox: [http://localhost:8025](http://localhost:8025) (only reachable from the host machine)
- Optional database admin UI: [http://localhost:8081](http://localhost:8081), if enabled (only reachable from the host machine)
- API docs (if available in this lab build): [http://localhost:18181/docs](http://localhost:18181/docs)

## Running the app

```bash
docker compose down -v
docker compose up --build
```

Main URLs:
- Main app: `http://localhost:18181`
- MailHog: `http://localhost:8025`
- Optional database admin UI: `http://localhost:8081`, if enabled

If phpPgAdmin is enabled, use:
- Server/Host: `db`
- Port: `5432`
- Database: `dat250`
- Username: `dat250`
- Password: `dat250`

## Security fixes (Assignment 2)

This version of DAT250 SecureApp fixes the vulnerabilities found in Assignment 1 plus additional issues:

| ID | Vulnerability | Fix |
|---|---|---|
| 4.1 | Stored XSS and session hijacking | Removed `\|safe` from all templates; session cookie is `HttpOnly` and `SameSite=Lax` |
| 4.2 | Role mass assignment in `/profile/update` | The role is no longer accepted from the profile form |
| 4.3 | SQL injection in `/admin/search-users` and `/courses/search` | Parameterized queries |
| 4.4 | User enumeration on login and password reset | Identical generic responses |
| 4.5 | Missing access control on `/admin/*` | Role check on every admin route; role taken from the session only |
| E1/E2 | IDOR on grades, messages and profiles | Ownership checks |
| E3 | Insecure configuration | Debug off, generic error page, no hardcoded secret, internal services bound to `127.0.0.1` |
| E4 | Unsalted SHA-256 passwords | bcrypt (cost 12) |
| E5 | SSRF in `/resources/import` | Login required, http/https only, host allowlist, no redirects |

## Running the security tests

The automated regression tests (pytest) run against the running application.

```bash
# 1. Start the application (see Quick start)
docker compose up --build

# 2. In another terminal, install the test dependencies
python -m pip install -r requirements-test.txt

# 3. Run the tests
python -m pytest
```

All tests should pass. Each test checks that an attack from Assignment 1 is blocked **and** that legitimate use still works.
The password hashing tests read the database on `127.0.0.1:5432`; override with `TEST_DATABASE_URL` if needed.

## 5. Test users
Use these accounts in the local lab environment:

- admin@dat250.local / Admin123
- teacher@dat250.local / Teacher123
- ta@dat250.local / TA123
- alice@student.uis.no / Alice123
- bob@student.uis.no / Bob123
- charlie@student.uis.no / Charlie123

## 6. Resetting the lab
```bash
docker compose down -v
docker compose up --build
```

Or use helper scripts (run from this project folder):
- macOS/Linux: `./dat250.sh reset` — wipes DB volumes and starts again (foreground).
- macOS/Linux: `./dat250.sh rebuild` — pulls images, rebuilds the backend image without cache, recreates containers in the background (keeps DB volume).
- Windows PowerShell: `.\dat250.ps1 reset` or `.\dat250.ps1 rebuild` — same meanings as above.

## 7. Ethical rules
- Use this lab only on your own local machine.
- Only test your own DAT250 lab instance.
- Do not test, scan, or attack UiS systems or any public system.
- Do not scan public IP addresses or other students' machines.
- Do not deploy this application publicly.

Students may use external course-approved tools (for example browser DevTools and interception proxies) as required by the course assignments.

## Running with Kali Linux

### Mode A: App and tools on the same machine

Use:
`http://localhost:18181`

### Mode B: App on physical laptop, Kali in VM

- Keep the app running on the host laptop with Docker.
- Find the host IP address reachable from Kali.
- Try the host-only adapter IP, bridged adapter IP, or default gateway depending on virtualization mode.
- Open from Kali:
  `http://<HOST-IP>:18181`

### Mode C: App in one VM, Kali in another VM

- Put both VMs on the same virtual network.
- Bridged or host-only networking is usually easiest.
- Start Docker inside the target VM.
- Find the target VM IP:
  `ip -4 addr`
- From Kali, open:
  `http://<TARGET-VM-IP>:18181`

## 8. Troubleshooting
- Docker not running: start Docker Desktop first.
- Port already in use: stop other services on 18181/8025/5432.
- App not updated: run `docker compose down -v` and rebuild.
- Database issues: use the reset command to recreate data.

## 9. What students submit
- Security test plan
- Findings with evidence
- Root cause explanation
- Code/config fix for selected issues
- Retest evidence
