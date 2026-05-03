# FureverSafe: Pet Shelter & Adoption Management Platform

> A comprehensive web platform for pet shelters to manage dog profiles, health records, adoption listings, and connect pet lovers with adoptable pets through an intelligent adoption matching system. Features AI chatbot support and integrated veterinary appointment scheduling.

---

## Quick Start

### Prerequisites
- **Python** 3.10+
- **pip** (Python package manager)
- **PostgreSQL** (Neon cloud database recommended)
- **Git** for version control

### 30-Second Setup

```bash
# 1. Clone and enter directory
git clone https://github.com/delyang-777/fureversafe.git
cd fureversafe

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
# Copy .env.example to .env and update DATABASE_URL and email settings
cp .env.example .env

# 5. Set up database
flask db upgrade

# 6. Run application
flask run
```

**Access the app**: http://localhost:5000

---

## System Architecture

### 🏗️ Backend Architecture (Flask)

**Location**: Root directory  
**Framework**: Flask 2.3.2  
**Database**: PostgreSQL via SQLAlchemy ORM  

**Entry Point**: `app.py`

**Key Components**:
- **Models** (`models.py`) - 11 database models (User, Dog, HealthRecord, Vaccination, Appointment, AdoptionListing, AdoptionApplication, LostFound, EducationalResource, Notification, ApprovalRequest)
- **Forms** (`forms.py`) - WTForms validation for all user inputs
- **Routes** (`app.py`) - Flask route handlers for all endpoints
- **Chatbot** (`chatbot_service.py`) - AI-powered 24/7 user support
- **Configuration** (`config.py`) - Database, email, upload settings

### 📱 Frontend

**Location**: `templates/` and `static/`  
**Templating**: Jinja2  
**Styling**: Bootstrap/Tailwind CSS  
**JavaScript**: Vanilla JS + chatbot widget  

**Key Templates**:
- `base.html` - Base layout with navbar and chatbot widget
- `index.html` - Landing/home page
- `auth/login.html`, `auth/register.html` - Authentication pages
- `dog_profile/` - Dog listing, creation, editing
- `adoption/` - Adoption listings and applications
- `lost_found/` - Lost & Found pet reports
- `education/` - Educational resources
- `dashboard.html` - User dashboard
- `chatbot_widget.html` - AI chatbot floating widget

### 🤖 AI Chatbot Integration

**Service**: `chatbot_service.py`  
**Endpoint**: `POST /api/chatbot`  
**UI**: Floating widget in bottom-right corner (always on)  
**Features**:
- 24/7 availability
- Context-aware responses
- Beautiful purple-themed UI matching FureverSafe branding
- Message history
- Responsive design (desktop, tablet, mobile)

See `CHATBOT_GUIDE.md` for detailed chatbot documentation.

### 🗄️ Database Models

| Model | Purpose | Key Fields |
|-------|---------|-----------|
| **User** | Owner/Shelter/Vet accounts | id, username, email, user_type, is_approved |
| **Dog** | Pet profiles | id, name, breed, age, weight, microchip_id, owner_id |
| **HealthRecord** | Veterinary checkups | id, dog_id, record_type, description, vet_name |
| **Vaccination** | Shot records | id, dog_id, vaccine_name, date_administered, next_due_date |
| **Appointment** | Vet appointments | id, dog_id, appointment_date, vet_name, location |
| **AdoptionListing** | Dogs available for adoption | id, shelter_id, dog_name, breed, age, description |
| **AdoptionApplication** | User adoption requests | id, listing_id, applicant_id, status |
| **LostFound** | Lost/found pet reports | id, reporter_id, pet_type, location, description |
| **EducationalResource** | Pet care articles | id, title, content, category |
| **Notification** | User notifications | id, user_id, message, is_read |
| **ApprovalRequest** | User approval workflow | id, user_id, status, user_type_requested |

---

## Installation & Setup

### 1. Clone Repository
```bash
git clone https://github.com/delyang-777/fureversafe.git
cd fureversafe
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

**Key Dependencies**:
- Flask 2.3.2 - Web framework
- Flask-SQLAlchemy 3.0.5 - ORM
- Flask-Login 0.6.2 - Authentication
- Flask-WTF 1.1.1 - Form security
- Flask-CKEditor 0.5.2 - Rich text editor
- python-dotenv 1.0.0 - Environment variables
- Gunicorn 21.2.0 - Production server

### 4. Environment Configuration

Create `.env` file in root directory:

```env
# Database
DATABASE_URL=postgresql://user:password@host/dbname
SQLALCHEMY_TRACK_MODIFICATIONS=False

# Security
SECRET_KEY=your-secret-key-change-in-production

# Email (Gmail SMTP)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password

# Upload settings
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=700971520  # 700MB
```

**For Neon Database** (PostgreSQL cloud):
```env
DATABASE_URL=postgresql://neondb_owner:PASSWORD@ep-xxxxx.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

### 5. Initialize Database
```bash
# Create migration (first time)
flask db init

# Apply migrations
flask db upgrade

# (Optional) Seed demo data
python add_sample_data.py
```

### 6. Create Admin User
```bash
python create_admin.py
# Prompts for username, email, password
```

---

## Running the Application

### Development Mode
```bash
flask run
# Accessible at http://localhost:5000
# With auto-reload on code changes
```

### Production Mode
```bash
# Using Gunicorn (4 workers)
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

---

## Project Structure

```
fureversafe/
├── .github/
│   └── agents/
│       └── fureversafe-analyzer.agent.md    # Custom VS Code agent
├── .env                                      # Environment configuration (create this)
├── requirements.txt                          # Python dependencies
├── README.md                                 # This file
├── CHATBOT_GUIDE.md                         # Chatbot setup & features
├── app.py                                   # Main Flask application
├── config.py                                # Configuration settings
├── models.py                                # SQLAlchemy database models
├── forms.py                                 # WTForms validation
├── chatbot_service.py                       # AI chatbot logic
├── create_admin.py                          # Admin account creation script
├── add_sample_data.py                       # Demo data insertion
├── create_all_templates.py                  # Template generation utility
├── reset_db.py                              # Database reset script
├── diagnose.py                              # Troubleshooting script
├── templates/                               # Jinja2 HTML templates
│   ├── base.html                           # Base layout
│   ├── index.html                          # Home page
│   ├── chatbot_widget.html                 # AI chatbot UI
│   ├── dashboard.html                      # User dashboard
│   ├── auth/                               # Login/Register
│   ├── adoption/                           # Adoption listings/apps
│   ├── dog_profile/                        # Dog CRUD pages
│   ├── lost_found/                         # Lost/Found reports
│   ├── education/                          # Educational resources
│   └── notifications.html                  # Notifications
├── static/                                  # Static files
│   ├── css/
│   │   ├── style.css                       # Main stylesheet
│   │   └── chatbot.css                     # Chatbot styling
│   ├── js/
│   │   └── main.js                         # Main JavaScript
│   └── uploads/                            # User uploaded files
├── instance/                                # Instance-specific files
│   └── dev.db                              # SQLite dev database (if used)
├── migrations/                              # Flask-Migrate database migrations
└── __pycache__/                            # Python cache

```

---

## Key Features

### 👥 User Management
- Multi-role authentication: Pet owners, shelters, veterinarians
- User registration and email verification
- Approval workflow for shelter/vet accounts
- Profile management with secure password hashing

### 🐕 Pet Management
- Dog profile creation with photos and videos
- Breed, age, weight, microchip tracking
- Health records (checkups, surgeries, notes)
- Vaccination schedules with automatic reminders
- Veterinary appointments with location tracking

### 🏠 Adoption System
- Shelters create adoption listings
- Pet owners apply for adoptions
- Application review and approval workflow
- Adoption status tracking

### 🔍 Lost & Found
- Report lost pets with photos and location
- Report found pets
- Community search and matching

### 📚 Educational Resources
- Rich-text educational articles (CKEditor)
- Pet care tips and guides
- Categorized by topic

### 💬 AI Chatbot
- 24/7 automated user support
- Context-aware responses
- Beautiful floating widget UI
- Available on all pages

### 📬 Notifications
- Email notifications for adoption applications
- Appointment reminders
- System updates

---

## Common Workflows

### Adding a New Dog Profile
1. Owner/Shelter logs in
2. Navigate to "Add Pet" or "My Dogs"
3. Fill form: name, breed, age, weight, microchip
4. Upload photos/videos
5. Save to database
6. Dog appears in listings

### Applying for Adoption
1. User views adoption listing
2. Clicks "Apply to Adopt"
3. Fills adoption application form
4. Shelter reviews application
5. Notification sent to applicant

### Creating Educational Article
1. Admin/Editor logs in
2. Navigate to "Create Article"
3. Use CKEditor to write content
4. Add category and metadata
5. Publish to make visible

### Registering Vet Appointment
1. Owner logs in
2. Navigate to dog profile
3. Click "Schedule Appointment"
4. Fill: date, time, vet name, location
5. Save to database
6. Reminder email sent before appointment

---

## Troubleshooting

### 1. "No module named 'flask'"
**Cause**: Virtual environment not activated or dependencies not installed  
**Fix**:
```bash
# Activate venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. "ModuleNotFoundError: No module named 'dotenv'"
**Fix**: `pip install python-dotenv`

### 3. "OperationalError: no such table"
**Cause**: Database not initialized  
**Fix**:
```bash
flask db init
flask db upgrade
```

### 4. "FATAL: database does not exist"
**Cause**: PostgreSQL database not created  
**Fix**: Create database in PostgreSQL or use Neon dashboard to provision

### 5. "Email sending fails"
**Cause**: Gmail credentials or app password incorrect  
**Fix**:
- Generate Gmail app password: https://myaccount.google.com/apppasswords
- Update `.env` with correct credentials
- Enable "Less secure apps" if using regular password (not recommended)

### 6. "File upload fails"
**Cause**: `static/uploads/` directory missing or permissions issue  
**Fix**:
```bash
mkdir -p static/uploads
chmod 755 static/uploads
```

### 7. "Form validation errors"
**Cause**: WTForms validation failed (invalid email, password too weak, etc.)  
**Fix**: Check form definitions in `forms.py` and error messages returned

### 8. "User not authenticated (None)"
**Cause**: Session expired or user not logged in  
**Fix**: Ensure routes use `@login_required` decorator and user is logged in

### 9. "Database migration conflicts"
**Cause**: Conflicting migrations after branch merge  
**Fix**:
```bash
flask db merge --rev-id xxx
flask db upgrade
```

---

## Development Tips

### Hot Reload
Flask auto-reloads on code changes during `flask run` (development mode). No manual restart needed for Python files.

### Database Debugging
```bash
# Check database schema
flask shell
>>> from models import Dog
>>> Dog.query.all()

# Run SQL directly
>>> from app import db
>>> db.session.execute("SELECT * FROM user;")
```

### Common Flask Commands
```bash
# Start shell for testing
flask shell

# Create migration after model change
flask db migrate -m "description"

# Apply migrations
flask db upgrade

# Downgrade database
flask db downgrade

# Drop all tables (CAUTION!)
flask shell
>>> from app import db
>>> db.drop_all()
```

### Debug Mode
Set `FLASK_ENV=development` to enable debug toolbar and better error pages:
```bash
export FLASK_ENV=development  # Linux/macOS
set FLASK_ENV=development     # Windows
flask run
```

---

## API Endpoints

### Authentication
- `POST /login` - User login
- `POST /register` - User registration
- `GET /logout` - User logout
- `POST /change_password` - Change password

### Dogs
- `GET /` - Home page with all dogs
- `GET /add_dog` - Add dog form
- `POST /add_dog` - Create new dog
- `GET /dog/<id>` - View dog profile
- `GET /edit_dog/<id>` - Edit dog form
- `POST /edit_dog/<id>` - Update dog
- `GET /delete_dog/<id>` - Delete dog

### Adoption
- `GET /adoptions` - Browse adoption listings
- `GET /create_listing` - Create adoption listing (shelter only)
- `POST /create_listing` - Submit listing
- `POST /apply/<id>` - Apply for adoption
- `GET /applications` - View applications

### Chatbot
- `POST /api/chatbot` - Send message to AI chatbot

### Educational Resources
- `GET /resources` - View educational articles
- `GET /create_resource` - Create article (admin only)
- `POST /create_resource` - Submit article

---

## Performance Optimizations

### Database
- Use indexed queries for frequently accessed data
- Enable connection pooling in production
- Consider caching for read-heavy operations

### Frontend
- Lazy load images/videos
- Minimize CSS/JavaScript
- Use CDN for static files in production

### Application
- Use Gunicorn with multiple workers for production
- Run behind Nginx reverse proxy
- Enable gzip compression

---

## Security Best Practices

✅ Always use environment variables for secrets  
✅ Enable CSRF protection (Flask-WTF does this automatically)  
✅ Use password hashing (Werkzeug.security handles this)  
✅ Validate all user inputs (WTForms validation)  
✅ Use HTTPS in production  
✅ Keep dependencies updated (`pip list --outdated`)  
✅ Never commit `.env` file to version control  

---

## Deployment

### Heroku
```bash
# Install Heroku CLI
# Login and create app
heroku create fureversafe-app

# Set environment variables
heroku config:set DATABASE_URL=postgresql://...
heroku config:set SECRET_KEY=your-secret-key

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

### AWS/DigitalOcean
1. Provision PostgreSQL database
2. Set environment variables on server
3. Run: `gunicorn -w 4 -b 0.0.0.0:8000 app:app`
4. Configure Nginx as reverse proxy
5. Set up SSL with Let's Encrypt

---

## Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes following Flask best practices
3. Test thoroughly before committing
4. Write clear commit messages
5. Open pull request with description

---

## Support & Resources

- **Flask Documentation**: https://flask.palletsprojects.com/
- **SQLAlchemy ORM**: https://docs.sqlalchemy.org/
- **Flask-Login**: https://flask-login.readthedocs.io/
- **PostgreSQL**: https://www.postgresql.org/docs/
- **Neon Database**: https://neon.tech/docs/

---

**Last Updated**: April 30, 2026  
**Repository**: https://github.com/delyang-777/fureversafe  
**License**: Check LICENSE file in repository
