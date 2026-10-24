# CollegeCollab 🎓

**A College Event Collaboration Platform**

CollegeCollab is a web-based platform designed to simplify college event management. It allows students to explore events and register for them, while organizers can create, manage, update, and cancel events.

## ✨ Features

* User registration and login
* Student and organizer roles
* College management
* Create, view, update, and delete events
* Student event registration and cancellation
* Registration count and attendee details for organizers
* Email notifications for event-related activities
* RESTful APIs using Django REST Framework
* JWT-based authentication
* API documentation with Swagger and ReDoc

## 🛠️ Technologies Used

* **Backend:** Python, Django
* **API:** Django REST Framework
* **Database:** PostgreSQL
* **Authentication:** JSON Web Tokens (JWT)
* **API Documentation:** drf-spectacular, Swagger UI, ReDoc
* **Frontend:** HTML, CSS, JavaScript
* **Email Service:** Gmail SMTP

## 📁 Project Structure

```text
CollegeCollab/
├── accounts/
├── colleges/
├── events/
├── feedback/
├── frontend/
├── notifications/
├── registrations/
├── config/
├── static/
├── templates/
├── manage.py
├── .gitignore
├── EMAIL_SETUP.md
└── README.md
```

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/kumkumpatidar26/CollegeCollab.git
cd CollegeCollab
```

### 2. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

Install the packages required by the project. If a `requirements.txt` file is available, run:

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root and configure the required values:

* `DJANGO_SECRET_KEY`
* `DJANGO_DEBUG`
* `DJANGO_ALLOWED_HOSTS`
* `DB_ENGINE`
* `DB_NAME`
* `DB_USER`
* `DB_PASSWORD`
* `DB_HOST`
* `DB_PORT`
* `GMAIL_ADDRESS`
* `GMAIL_APP_PASSWORD`

Keep real credentials private. See `EMAIL_SETUP.md` for detailed configuration instructions.

### 5. Run database migrations

```powershell
python manage.py migrate
```

### 6. Start the development server

```powershell
python manage.py runserver
```

Open the application at:

http://127.0.0.1:8000/

## 📚 API Documentation

When the development server is running:

* **Swagger UI:** http://127.0.0.1:8000/api/docs/
* **ReDoc:** http://127.0.0.1:8000/api/redoc/

## 🔐 Security Notes

* Never commit `.env` files or real credentials.
* Keep Django's `DEBUG` setting disabled in production.
* Configure `ALLOWED_HOSTS` appropriately before deployment.
* Use secure credentials and HTTPS for production deployments.

## 🚀 Future Improvements

* Improve organizer notification display
* Add further testing and validation
* Deploy the application to a production hosting platform

## 👩‍💻 Project Status

CollegeCollab is an academic mini-project under development.
