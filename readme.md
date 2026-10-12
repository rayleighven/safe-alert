<div align="center">
  <img src="frontend/src/assets/images/safe-alert-logo.png" alt="SAFE-ALERT logo" width="112" />
  <h1>SAFE-ALERT</h1>
  <p><strong>Community disaster preparedness and response for Baclayon, Bohol</strong></p>
  <p>Household readiness · Evacuation coordination · Hazard information · Emergency updates</p>
</div>

---

## About

SAFE-ALERT is a disaster preparedness and response information system for Barangay Cambanac and Barangay Poblacion in Baclayon, Bohol. It gives authorized barangay and municipal personnel a shared place to organize readiness information and coordinate updates for residents.

## What SAFE-ALERT does

| Area | Capabilities |
| --- | --- |
| **Household readiness** | Household and family-member records, vulnerability information, and evacuation prioritization. |
| **Evacuation centers** | Center details, capacity and occupancy tracking, and check-in records. |
| **Hazard information** | Hazard map references and interactive hazard maps. |
| **Community updates** | Announcements and advisories, plus SMS broadcast staging, authorization, and delivery logs. SMS runs in dry-run mode by default; real messages require explicit configuration. |
| **Monitoring** | Dashboards and reports for authorized roles. |

Access is role-based for Barangay Secretaries, Barangay Kagawad/Tanod, Barangay Healthworkers, BDRRMC Chairpersons, MDRRMO Officers, and Residents.

## Technology

| Layer | Technology |
| --- | --- |
| Frontend | Vue 3, Vite, and Tailwind CSS |
| API | Django REST Framework |
| Database | PostgreSQL |

## Contents

- [Run SAFE-ALERT on another PC](#run-safe-alert-on-another-pc)
- [Requirements](#requirements)
- [Create the local database](#1-create-a-local-postgresql-database)
- [Configure the backend on Windows](#2-configure-and-start-the-backend-powershell)
- [Create your own local account](#3-create-your-own-local-system-account)
- [Configure the frontend](#4-configure-and-start-the-frontend)
- [macOS/Linux setup](#macoslinux-equivalents)
- [Later runs](#later-runs)
- [Notes](#notes)

## Run SAFE-ALERT on another PC

Each developer needs a local PostgreSQL database and two terminal windows. The commands below use PowerShell on Windows; equivalent steps for macOS/Linux are included afterward.

## Requirements

- Python 3.12 or newer
- Node.js 22.12 or newer (npm is included)
- PostgreSQL 15 or newer, with the PostgreSQL command-line tools available
- A copy of this repository

## 1. Create a local PostgreSQL database

Open `psql` as a PostgreSQL administrator (for example, `psql -U postgres`) and run these SQL commands once:

```sql
CREATE USER safealert_user WITH PASSWORD 'choose-a-local-password';
CREATE DATABASE safealert OWNER safealert_user;
```

Exit `psql` with `\q`. Replace the example password with your own local password.

## 2. Configure and start the backend (PowerShell)

From the repository root, create and activate a Python virtual environment, install the backend dependencies, and write a local environment file:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

$secret = python -c "import secrets; print(secrets.token_urlsafe(50))"
@"
DJANGO_SECRET_KEY=$secret
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=safealert
DB_USER=safealert_user
DB_PASSWORD=choose-a-local-password
DB_HOST=127.0.0.1
DB_PORT=5432
CORS_ALLOWED_ORIGINS=http://localhost:5173
CSRF_TRUSTED_ORIGINS=http://localhost:5173
SMS_DRY_RUN=True
"@ | Set-Content -Encoding ascii .env

python manage.py migrate
python manage.py runserver
```

Set `DB_PASSWORD` to the same password used when creating the PostgreSQL user. Keep this terminal open. The API runs at `http://127.0.0.1:8000/`.

## 3. Create your own local system account

SAFE-ALERT has no public self-registration. Each developer should create a unique local account; do not share or recreate the old sample accounts. On a fresh database, create the barangay record that the account will belong to. The login page currently supports the Cambanac and Poblacion areas, so use the matching official barangay name and real contact number. Open a separate backend terminal at the repository root:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python manage.py shell
```

At the Python prompt, create the barangay if it is not already present. Replace the contact number with the correct local number:

```python
from core.models import Barangay

Barangay.objects.get_or_create(
    name='Cambanac',
    defaults={
        'municipality': 'Baclayon',
        'province': 'Bohol',
        'contact_number': 'REPLACE_WITH_REAL_CONTACT_NUMBER',
    },
)
```

Use `name='Poblacion'` instead if that is the account's barangay. Exit the shell with `exit()`. Then create your own initial Secretary account:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python manage.py createsuperuser
```

Enter your own username, email, and strong password when prompted. The project assigns this initial account the Barangay Secretary role. Attach it to the barangay you created or found by replacing `YOUR_USERNAME` and the barangay name in this command:

```powershell
python manage.py shell -c "from accounts.models import User; from core.models import Barangay; user = User.objects.get(username='YOUR_USERNAME'); user.barangay = Barangay.objects.get(name='Cambanac'); user.save(update_fields=['barangay'])"
```

Use `Poblacion` in the command if that is the account's barangay. Run `createsuperuser` only to create your own trusted local administrator/Secretary account. After signing in, that Secretary can add separate accounts for other roles from **Accounts**. Do not reuse another developer's credentials.

### Optional: fill the dashboard with local demo data

To preview the dashboard with records, open a backend terminal after creating your own active Barangay Secretary account and run:

```powershell
cd backend
python manage.py seed_dashboard_demo --barangay Poblacion
```

This creates 10 fictional Resident accounts (`demo_resident_01` through `demo_resident_10`) and links them to sample households in **Barangay Poblacion**. It also creates demo vulnerability assessments, evacuation centers, Project NOAH map references, announcements, and SMS delivery records. The SMS records are local samples; no messages are sent. Demo content is labeled `DEMO` in the system.

The command only runs while `DJANGO_DEBUG=True`. Each new account gets a random password printed to that backend terminal. Save those credentials locally; do not commit or share the terminal output. For existing demo accounts, use `python manage.py seed_dashboard_demo --barangay Poblacion --reset-passwords` to generate and print new passwords. To remove only the demo data and accounts, run `python manage.py seed_dashboard_demo --clear`.

The seeder source is safe to upload to GitHub: it contains no reusable account password, runs only when Django debug mode is enabled, and is not run automatically during setup. Keep `.env` files, database dumps, and generated login credentials out of the repository. Use a Poblacion Secretary account to view the aggregate dashboard data; the Resident accounts can only view their linked households.

Keep using your Secretary account to see the complete household analytics dashboard. Resident accounts are scoped to their linked household.

## 4. Configure and start the frontend

Open a second terminal at the repository root:

```powershell
cd frontend
@"
VITE_API_BASE_URL=http://127.0.0.1:8000/api/
"@ | Set-Content -Encoding ascii .env.local
npm ci
npm run dev
```

Open the local URL Vite prints (normally `http://localhost:5173/`). Keep both the frontend and backend terminals running while using the app.

## macOS/Linux equivalents

Create the backend environment and local settings from the repository root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cat > .env <<EOF
DJANGO_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(50))')
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=safealert
DB_USER=safealert_user
DB_PASSWORD=choose-a-local-password
DB_HOST=127.0.0.1
DB_PORT=5432
CORS_ALLOWED_ORIGINS=http://localhost:5173
CSRF_TRUSTED_ORIGINS=http://localhost:5173
SMS_DRY_RUN=True
EOF
python manage.py migrate
python manage.py runserver
```

Before using the app, create a unique initial local Secretary account in a separate backend terminal. Ensure the barangay exists first; use the real contact number for your local setup:

```bash
cd backend
source .venv/bin/activate
python manage.py shell <<'PY'
from core.models import Barangay
Barangay.objects.get_or_create(
    name='Cambanac',
    defaults={
        'municipality': 'Baclayon',
        'province': 'Bohol',
        'contact_number': 'REPLACE_WITH_REAL_CONTACT_NUMBER',
    },
)
PY
python manage.py createsuperuser
python manage.py shell -c "from accounts.models import User; from core.models import Barangay; user = User.objects.get(username='YOUR_USERNAME'); user.barangay = Barangay.objects.get(name='Cambanac'); user.save(update_fields=['barangay'])"
```

Replace `REPLACE_WITH_REAL_CONTACT_NUMBER`, `YOUR_USERNAME`, and `Cambanac` as appropriate. `createsuperuser` prompts for the account's username, email, and password. The first account is a Secretary; use **Accounts** in the app to create additional role accounts. Each developer should use their own credentials.

In another terminal at the repository root:

```bash
cd frontend
printf 'VITE_API_BASE_URL=http://127.0.0.1:8000/api/\n' > .env.local
npm ci
npm run dev
```

Use the account-creation commands above when initializing another local database. Every developer should use their own username and password.

## Later runs

Start PostgreSQL first. Then use one terminal for the backend (`cd backend`, activate `.venv`, `python manage.py runserver`) and another for the frontend (`cd frontend`, `npm run dev`). The `.env` and `.env.local` files only need to be created once per checkout.

## Notes

- Uploaded media is stored in `backend/media/`; the local development server serves it when debug mode is enabled.
- The SMS gateway is in dry-run mode by default. Do not set `SMS_DRY_RUN=False` unless an authorized Semaphore API key is configured and real SMS sending is intended.
- These runserver settings are for local development, not production hosting. Do not expose Django's development server to the public internet.
- If the frontend cannot reach the API, confirm both servers are running and that `VITE_API_BASE_URL`, `CORS_ALLOWED_ORIGINS`, and `CSRF_TRUSTED_ORIGINS` match the local addresses above.
