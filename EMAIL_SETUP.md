# Gmail email setup

CollegeCollab uses Django's SMTP backend with Gmail. The project reads its
secret key, PostgreSQL credentials, and Gmail credentials from environment
variables; it does not load a `.env` file.

## Configure PowerShell

Set these values in the PowerShell window used to run Django. Generate a
`DJANGO_SECRET_KEY` locally with:

```powershell
.\.venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Then set the environment variables, replacing placeholders with your own
values. `DB_ENGINE` can be omitted for the PostgreSQL default.

```powershell
$env:DJANGO_SECRET_KEY = "<generated secret key>"
$env:DJANGO_DEBUG = "true"
$env:DJANGO_ALLOWED_HOSTS = "localhost,127.0.0.1"
$env:DB_ENGINE = "django.db.backends.postgresql"
$env:DB_NAME = "<PostgreSQL database name>"
$env:DB_USER = "<PostgreSQL user>"
$env:DB_PASSWORD = "<PostgreSQL password>"
$env:DB_HOST = "localhost"
$env:DB_PORT = "5432"
$env:GMAIL_ADDRESS = "<your Gmail address>"
$env:GMAIL_APP_PASSWORD = "<Google app password>"
```

Enable 2-Step Verification on the Google account, create an App Password, and
use that password rather than the account password. Keep the values out of
source control and rotate any credentials that were previously committed.

## Run the project

From the project directory, after configuring the variables above:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

## Run tests

The tests use Django's in-memory email backend. To run them without requiring
a running PostgreSQL server, set the database to in-memory SQLite for that
PowerShell window:

```powershell
$env:DB_ENGINE = "django.db.backends.sqlite3"
$env:DB_NAME = ":memory:"
.\.venv\Scripts\python.exe manage.py test
```

To run against PostgreSQL instead, set `DB_ENGINE` back to
`django.db.backends.postgresql` and provide the PostgreSQL values above. The
test email backend does not contact Gmail.

## Verify actual Gmail delivery

Configure `GMAIL_ADDRESS` and `GMAIL_APP_PASSWORD` as above, keep
`DB_ENGINE` set to PostgreSQL, then run the server. Sign in as a student and
register for an event using the application's registration endpoint. Check
the recipient mailbox and spam folder for the confirmation. Try canceling the
registration and updating/canceling an event to verify the other messages.
SMTP credentials are not returned by the API or written to application logs.
