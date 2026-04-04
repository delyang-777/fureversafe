from flask import Flask, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
import json
from wtforms import form
from config import Config
from models import ApprovalRequest, db, User, Dog, HealthRecord, Vaccination, Appointment, AdoptionListing, AdoptionApplication, LostFound, EducationalResource, Notification
from forms import *
from flask_migrate import Migrate
from flask_mail import Mail, Message
from flask_ckeditor import CKEditor
import markdown
from markdown.extensions.extra import ExtraExtension
from markdown.extensions.codehilite import CodeHiliteExtension
from werkzeug.utils import secure_filename
from flask import request, current_app

# Fix: Specify the template folder explicitly with absolute path
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

app = Flask(__name__, 
           template_folder=template_dir,
           static_folder=static_dir)

app.config.from_object(Config)
app.config['MAX_CONTENT_LENGTH'] = 700 * 1024 * 1024  # 700MB max file size

ckeditor = CKEditor(app)

# CKEditor configuration
app.config['CKEDITOR_SERVE_LOCAL'] = True
app.config['CKEDITOR_HEIGHT'] = 400
app.config['CKEDITOR_WIDTH'] = '100%'
app.config['CKEDITOR_ENABLE_CODESNIPPET'] = True

app.config.from_object(Config)

# Configure email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_password'
mail = Mail(app)

# In registration route, after creating user:
def send_approval_notification_to_shelters(user):
    shelters = User.query.filter_by(user_type='shelter', is_approved=True).all()
    for shelter in shelters:
        msg = Message(
            'New User Registration Needs Approval',
            sender='noreply@fureversafe.com',
            recipients=[shelter.email]
        )
        msg.body = f"""
        A new user has registered and needs approval:
        
        Username: {user.username}
        Email: {user.email}
        Type: {user.user_type}
        
        Please login to the approval dashboard to review this request.
        
        {url_for('approval_dashboard', _external=True)}
        """
        mail.send(msg)
        
def save_media_file(file):
    """Save uploaded image or video file"""
    if file and file.filename:
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        filename = f"media_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filename
    return None


# Add this after creating app
migrate = Migrate(app, db)

# Debug: Print template folder location
print(f"Template folder path: {app.template_folder}")
print(f"Template folder exists: {os.path.exists(app.template_folder)}")
print(f"Static folder path: {app.static_folder}")
print(f"Static folder exists: {os.path.exists(app.static_folder)}")

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.template_folder, 'adoption'), exist_ok=True)
os.makedirs(os.path.join(app.template_folder, 'lost_found'), exist_ok=True)
os.makedirs(os.path.join(app.template_folder, 'education'), exist_ok=True)
os.makedirs(os.path.join(app.template_folder, 'dog_profile'), exist_ok=True)
os.makedirs(os.path.join(app.template_folder, 'auth'), exist_ok=True)
os.makedirs(os.path.join(app.template_folder, 'shelter'), exist_ok=True)

@login_manager.user_loader
def load_user(user_id):
    # Use db.session.get() instead of Query.get() (SQLAlchemy 2.0 compatible)
    return db.session.get(User, int(user_id))

# Helper function to save uploaded file
def save_file(file):
    if file and file.filename:
        filename = secure_filename(file.filename)
        # Add timestamp to filename to avoid collisions
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filename
    return None

# Helper function to check if user can access dog
def can_access_dog(dog_id):
    dog = Dog.query.get_or_404(dog_id)
    if current_user.user_type == 'owner' and dog.owner_id == current_user.id:
        return True
    elif current_user.user_type in ['shelter', 'vet']:
        return True
    return False

# Notification Functions
def create_notification(user_id, title, message, type=None, reference_id=None):
    """Create a notification for a user"""
    try:
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type,
            reference_id=reference_id
        )
        db.session.add(notification)
        db.session.commit()
        return notification
    except Exception as e:
        print(f"Error creating notification: {e}")
        db.session.rollback()
        return None

def notify_all_users(title, message, type=None, reference_id=None, user_types=None):
    """Send notification to all users or specific user types"""
    query = User.query
    if user_types:
        query = query.filter(User.user_type.in_(user_types))
    
    users = query.all()
    notifications = []
    for user in users:
        notification = Notification(
            user_id=user.id,
            title=title,
            message=message,
            type=type,
            reference_id=reference_id
        )
        notifications.append(notification)
    
    db.session.add_all(notifications)
    db.session.commit()
    return len(notifications)

def notify_shelters(title, message, type=None, reference_id=None):
    """Notify all shelter users"""
    return notify_all_users(title, message, type, reference_id, user_types=['shelter'])

def notify_owners(title, message, type=None, reference_id=None):
    """Notify all dog owners"""
    return notify_all_users(title, message, type, reference_id, user_types=['owner'])

def notify_vets(title, message, type=None, reference_id=None):
    """Notify all veterinarians"""
    return notify_all_users(title, message, type, reference_id, user_types=['vet'])

# Routes
@app.route('/')
def index():
    recent_listings = AdoptionListing.query.filter_by(status='available').order_by(AdoptionListing.created_at.desc()).limit(6).all()
    recent_resources = EducationalResource.query.order_by(EducationalResource.created_at.desc()).limit(3).all()
    recent_lost_found = LostFound.query.filter_by(status='active').order_by(LostFound.created_at.desc()).limit(5).all()
    return render_template('index.html', 
                         recent_listings=recent_listings,
                         recent_resources=recent_resources,
                         recent_lost_found=recent_lost_found)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if user exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))
        
        # Create user with approval pending
        user = User(
            username=form.username.data,
            email=form.email.data,
            user_type=form.user_type.data,
            is_approved=False  # Not approved by default
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.flush()  # Get user ID without committing
        
        # Create approval request
        approval_request = ApprovalRequest(
            user_id=user.id,
            requested_by=user.id,
            user_type_requested=form.user_type.data,
            reason=form.reason.data
        )
        db.session.add(approval_request)
        
        db.session.commit()
        
        # Notify shelters about new registration
        notify_shelters(
            title='New User Registration Pending',
            message=f'New user {user.username} has registered and needs approval.',
            type='approval',
            reference_id=user.id
        )
        
        flash('Registration request submitted! Please wait for approval from an organization/shelter.', 'info')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            # Check if user is approved
            if not user.is_approved:
                flash('Your account is pending approval. Please wait for an administrator to approve your account.', 'warning')
                return redirect(url_for('login'))
            
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            
            # Redirect based on user type
            if user.user_type == 'shelter':
                return redirect(url_for('approval_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('auth/login.html', form=form)

@app.route('/approval-dashboard')
@login_required
def approval_dashboard():
    # Only shelters can access this
    if current_user.user_type != 'shelter':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get pending approval requests
    pending_requests = ApprovalRequest.query.filter_by(status='pending').all()
    
    # Get approved users
    approved_users = User.query.filter(User.is_approved == True, User.user_type.in_(['owner', 'vet'])).all()
    
    return render_template('shelter/approval_dashboard.html', 
                         pending_requests=pending_requests,
                         approved_users=approved_users)

@app.route('/approve-user/<int:request_id>', methods=['POST'])
@login_required
def approve_user(request_id):
    if current_user.user_type != 'shelter':
        abort(403)
    
    approval_request = ApprovalRequest.query.get_or_404(request_id)
    
    if approval_request.status != 'pending':
        flash('This request has already been processed.', 'warning')
        return redirect(url_for('approval_dashboard'))
    
    # Approve the user
    user = User.query.get(approval_request.user_id)
    user.is_approved = True
    user.approved_by = current_user.id
    user.approved_at = datetime.now()
    
    # Update approval request
    approval_request.status = 'approved'
    approval_request.reviewed_by = current_user.id
    approval_request.reviewed_at = datetime.now()
    
    db.session.commit()
    
    # Notify the user that they've been approved
    create_notification(
        user_id=user.id,
        title='Account Approved!',
        message=f'Your account has been approved by {current_user.username}. You can now log in.',
        type='approval',
        reference_id=user.id
    )
    
    flash(f'User {user.username} has been approved!', 'success')
    return redirect(url_for('approval_dashboard'))

@app.route('/reject-user/<int:request_id>', methods=['POST'])
@login_required
def reject_user(request_id):
    if current_user.user_type != 'shelter':
        abort(403)
    
    approval_request = ApprovalRequest.query.get_or_404(request_id)
    reason = request.form.get('rejection_reason', '')
    
    if approval_request.status != 'pending':
        flash('This request has already been processed.', 'warning')
        return redirect(url_for('approval_dashboard'))
    
    # Update approval request
    approval_request.status = 'rejected'
    approval_request.reviewed_by = current_user.id
    approval_request.reviewed_at = datetime.now()
    
    # Optionally delete the user or just mark as rejected
    user = User.query.get(approval_request.user_id)
    
    db.session.commit()
    
    flash(f'User {user.username} has been rejected.', 'info')
    return redirect(url_for('approval_dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    dogs = Dog.query.filter_by(owner_id=current_user.id).all() if current_user.user_type == 'owner' else []
    upcoming_appointments = []
    if current_user.user_type == 'owner':
        for dog in dogs:
            upcoming_appointments.extend(Appointment.query.filter_by(dog_id=dog.id)
                                       .filter(Appointment.appointment_date > datetime.now())
                                       .order_by(Appointment.appointment_date).limit(5).all())
    
    # For shelters, show adoption listings
    adoption_listings = []
    if current_user.user_type == 'shelter':
        adoption_listings = AdoptionListing.query.filter_by(shelter_id=current_user.id).order_by(AdoptionListing.created_at.desc()).limit(5).all()
    
    # For all users, show recent lost/found reports
    recent_reports = LostFound.query.filter_by(status='active').order_by(LostFound.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         dogs=dogs,
                         upcoming_appointments=upcoming_appointments,
                         adoption_listings=adoption_listings,
                         recent_reports=recent_reports)

# Dog Profile Management Routes
@app.route('/dog/create', methods=['GET', 'POST'])
@login_required
def create_dog():
    if current_user.user_type != 'owner':
        flash('Only dog owners can create dog profiles.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = DogProfileForm()
    if form.validate_on_submit():
        photo_filename = save_file(form.photo.data)
        
        dog = Dog(
            name=form.name.data,
            breed=form.breed.data,
            age=form.age.data,
            weight=form.weight.data,
            microchip_id=form.microchip_id.data,
            photo=photo_filename,
            owner_id=current_user.id
        )
        
        db.session.add(dog)
        db.session.commit()
        
        flash(f'Dog profile for {dog.name} created successfully!', 'success')
        return redirect(url_for('view_dog', dog_id=dog.id))
    
    return render_template('dog_profile/create.html', form=form)

@app.route('/dog/<int:dog_id>')
@login_required
def view_dog(dog_id):
    dog = Dog.query.get_or_404(dog_id)
    if not can_access_dog(dog_id) and dog.owner_id != current_user.id:
        abort(403)
    
    health_records = HealthRecord.query.filter_by(dog_id=dog_id).order_by(HealthRecord.date.desc()).all()
    vaccinations = Vaccination.query.filter_by(dog_id=dog_id).order_by(Vaccination.date_administered.desc()).all()
    appointments = Appointment.query.filter_by(dog_id=dog_id).order_by(Appointment.appointment_date).all()
    
    # Pass current datetime to template for comparison
    now = datetime.now()
    
    return render_template('dog_profile/view.html', 
                         dog=dog, 
                         health_records=health_records,
                         vaccinations=vaccinations,
                         appointments=appointments,
                         now=now)

@app.route('/dog/<int:dog_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_dog(dog_id):
    dog = Dog.query.get_or_404(dog_id)
    if dog.owner_id != current_user.id:
        abort(403)
    
    form = DogProfileForm()
    if form.validate_on_submit():
        dog.name = form.name.data
        dog.breed = form.breed.data
        dog.age = form.age.data
        dog.weight = form.weight.data
        dog.microchip_id = form.microchip_id.data
        
        if form.photo.data:
            photo_filename = save_file(form.photo.data)
            if photo_filename:
                dog.photo = photo_filename
        
        db.session.commit()
        flash('Dog profile updated successfully!', 'success')
        return redirect(url_for('view_dog', dog_id=dog.id))
    
    # Pre-populate form
    form.name.data = dog.name
    form.breed.data = dog.breed
    form.age.data = dog.age
    form.weight.data = dog.weight
    form.microchip_id.data = dog.microchip_id
    
    return render_template('dog_profile/edit.html', form=form, dog=dog)

@app.route('/dog/<int:dog_id>/delete', methods=['POST'])
@login_required
def delete_dog(dog_id):
    dog = Dog.query.get_or_404(dog_id)
    if dog.owner_id != current_user.id:
        abort(403)
    
    dog_name = dog.name
    db.session.delete(dog)
    db.session.commit()
    
    flash(f'{dog_name}\'s profile has been deleted.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/dog/<int:dog_id>/vaccination/add', methods=['POST'])
@login_required
def add_vaccination(dog_id):
    dog = Dog.query.get_or_404(dog_id)
    if dog.owner_id != current_user.id and current_user.user_type != 'vet':
        abort(403)
    
    try:
        vaccine_name = request.form.get('vaccine_name')
        date_administered_str = request.form.get('date_administered')
        next_due_date_str = request.form.get('next_due_date')
        administered_by = request.form.get('administered_by')
        
        if not vaccine_name or not date_administered_str:
            flash('Vaccine name and date administered are required.', 'danger')
            return redirect(url_for('view_dog', dog_id=dog_id))
        
        # Parse dates
        date_administered = datetime.strptime(date_administered_str, '%Y-%m-%dT%H:%M')
        next_due_date = None
        if next_due_date_str:
            next_due_date = datetime.strptime(next_due_date_str, '%Y-%m-%dT%H:%M')
        
        vaccination = Vaccination(
            dog_id=dog_id,
            vaccine_name=vaccine_name,
            date_administered=date_administered,
            next_due_date=next_due_date,
            administered_by=administered_by
        )
        
        db.session.add(vaccination)
        db.session.commit()
        flash('Vaccination record added successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding vaccination: {str(e)}', 'danger')
    
    return redirect(url_for('view_dog', dog_id=dog_id))

@app.route('/dog/<int:dog_id>/appointment/add', methods=['POST'])
@login_required
def add_appointment(dog_id):
    dog = Dog.query.get_or_404(dog_id)
    if dog.owner_id != current_user.id and current_user.user_type != 'vet':
        abort(403)
    
    try:
        appointment_type = request.form.get('appointment_type')
        appointment_date_str = request.form.get('appointment_date')
        vet_name = request.form.get('vet_name')
        location = request.form.get('location')
        notes = request.form.get('notes')
        
        # Validate required fields
        if not appointment_type or not appointment_date_str:
            flash('Appointment type and date are required.', 'danger')
            return redirect(url_for('view_dog', dog_id=dog_id))
        
        # Parse the date
        try:
            appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%dT%H:%M')
        except:
            flash('Invalid date format. Please use the date picker.', 'danger')
            return redirect(url_for('view_dog', dog_id=dog_id))
        
        # Check if date is in the future
        if appointment_date <= datetime.now():
            flash('Appointment date must be in the future.', 'danger')
            return redirect(url_for('view_dog', dog_id=dog_id))
        
        # Create appointment
        appointment = Appointment(
            dog_id=dog_id,
            appointment_type=appointment_type,
            appointment_date=appointment_date,
            vet_name=vet_name,
            location=location,
            notes=notes
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        # Notify dog owner
        create_notification(
            user_id=dog.owner_id,
            title='Appointment Scheduled',
            message=f'Appointment scheduled for {dog.name} on {appointment.appointment_date.strftime("%Y-%m-%d %H:%M")}',
            type='appointment',
            reference_id=appointment.id
        )
        
        flash('Appointment scheduled successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error scheduling appointment: {str(e)}', 'danger')
    
    return redirect(url_for('view_dog', dog_id=dog_id))

@app.route('/dog/<int:dog_id>/health-record/add', methods=['POST'])
@login_required
def add_health_record(dog_id):
    dog = Dog.query.get_or_404(dog_id)
    if dog.owner_id != current_user.id and current_user.user_type != 'vet':
        abort(403)
    
    try:
        # Get form data directly from request
        record_type = request.form.get('record_type')
        description = request.form.get('description')
        date_str = request.form.get('date')
        vet_name = request.form.get('vet_name')
        notes = request.form.get('notes')
        
        # Validate required fields
        if not record_type:
            flash('Record type is required.', 'danger')
            return redirect(url_for('view_dog', dog_id=dog_id))
        
        if not description:
            flash('Description is required.', 'danger')
            return redirect(url_for('view_dog', dog_id=dog_id))
        
        if not date_str:
            flash('Date is required.', 'danger')
            return redirect(url_for('view_dog', dog_id=dog_id))
        
        # Parse the date
        try:
            # Handle different date formats
            if 'T' in date_str:
                record_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            else:
                record_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
        except Exception as e:
            flash(f'Invalid date format: {str(e)}', 'danger')
            return redirect(url_for('view_dog', dog_id=dog_id))
        
        # Create health record
        health_record = HealthRecord(
            dog_id=dog_id,
            record_type=record_type,
            description=description,
            date=record_date,
            vet_name=vet_name,
            notes=notes
        )
        
        db.session.add(health_record)
        db.session.commit()
        flash('Health record added successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        print(f"Error adding health record: {e}")
        flash(f'Error adding health record: {str(e)}', 'danger')
    
    return redirect(url_for('view_dog', dog_id=dog_id))

# Adoption Module Routes
@app.route('/adoptions')
def adoption_listings():
    page = request.args.get('page', 1, type=int)
    listings = AdoptionListing.query.filter_by(status='available').order_by(AdoptionListing.created_at.desc()).paginate(page=page, per_page=12)
    return render_template('adoption/listings.html', listings=listings)

@app.route('/adoption/create', methods=['GET', 'POST'])
@login_required
def create_adoption_listing():
    if current_user.user_type != 'shelter':
        flash('Only shelters can create adoption listings.', 'warning')
        return redirect(url_for('dashboard'))
    
    form = AdoptionListingForm()
    if form.validate_on_submit():
        photo_filename = save_file(form.photo.data)
        
        listing = AdoptionListing(
            shelter_id=current_user.id,
            dog_name=form.dog_name.data,
            breed=form.breed.data,
            age=form.age.data,
            gender=form.gender.data,
            size=form.size.data,
            description=form.description.data,
            photo=photo_filename
        )
        
        db.session.add(listing)
        db.session.commit()
        
        # Notify all users about new adoption listing
        notify_all_users(
            title='New Dog Available for Adoption!',
            message=f'A new dog named {form.dog_name.data} is now available for adoption.',
            type='adoption',
            reference_id=listing.id
        )
        
        flash('Adoption listing created successfully!', 'success')
        return redirect(url_for('adoption_listings'))
    
    return render_template('adoption/create.html', form=form)

@app.route('/adoption/<int:listing_id>')
def view_adoption_listing(listing_id):
    listing = AdoptionListing.query.get_or_404(listing_id)
    return render_template('adoption/details.html', listing=listing)

@app.route('/adoption/<int:listing_id>/apply', methods=['GET', 'POST'])
@login_required
def apply_for_adoption(listing_id):
    listing = AdoptionListing.query.get_or_404(listing_id)
    
    if listing.status != 'available':
        flash('This dog is no longer available for adoption.', 'warning')
        return redirect(url_for('adoption_listings'))
    
    # Check if already applied
    existing_application = AdoptionApplication.query.filter_by(
        listing_id=listing_id, 
        applicant_id=current_user.id
    ).first()
    
    if existing_application:
        flash('You have already applied for this dog.', 'info')
        return redirect(url_for('view_adoption_listing', listing_id=listing_id))
    
    form = AdoptionApplicationForm()
    if form.validate_on_submit():
        application = AdoptionApplication(
            listing_id=listing_id,
            applicant_id=current_user.id,
            message=form.message.data
        )
        db.session.add(application)
        db.session.commit()
        
        # Notify shelter about new application
        create_notification(
            user_id=listing.shelter_id,
            title='New Adoption Application',
            message=f'{current_user.username} has applied to adopt {listing.dog_name}.',
            type='adoption',
            reference_id=application.id
        )
        
        flash('Your adoption application has been submitted!', 'success')
        return redirect(url_for('adoption_listings'))
    
    return render_template('adoption/apply.html', form=form, listing=listing)

@app.route('/adoption/applications')
@login_required
def view_applications():
    if current_user.user_type == 'shelter':
        # Shelters see applications for their listings
        applications = AdoptionApplication.query.join(AdoptionListing).filter(
            AdoptionListing.shelter_id == current_user.id
        ).order_by(AdoptionApplication.applied_at.desc()).all()
    else:
        # Owners see their applications
        applications = AdoptionApplication.query.filter_by(
            applicant_id=current_user.id
        ).order_by(AdoptionApplication.applied_at.desc()).all()
    
    return render_template('adoption/applications.html', applications=applications)

@app.route('/adoption/application/<int:app_id>/<action>')
@login_required
def process_application(app_id, action):
    if current_user.user_type != 'shelter':
        abort(403)
    
    application = AdoptionApplication.query.get_or_404(app_id)
    listing = AdoptionListing.query.get(application.listing_id)
    
    if listing.shelter_id != current_user.id:
        abort(403)
    
    if action == 'approve':
        application.status = 'approved'
        listing.status = 'pending'  # Mark as pending adoption
        flash('Application approved!', 'success')
    elif action == 'reject':
        application.status = 'rejected'
        flash('Application rejected.', 'info')
    else:
        flash('Invalid action.', 'danger')
        return redirect(url_for('view_applications'))
    
    application.reviewed_at = datetime.now()
    db.session.commit()
    
    # Notify applicant about decision
    create_notification(
        user_id=application.applicant_id,
        title=f'Adoption Application {action}d',
        message=f'Your application to adopt {listing.dog_name} has been {action}d.',
        type='adoption',
        reference_id=application.id
    )
    
    return redirect(url_for('view_applications'))

# Lost and Found Module Routes
@app.route('/lost-found')
def lost_found_reports():
    type_filter = request.args.get('type', 'all')
    page = request.args.get('page', 1, type=int)
    
    query = LostFound.query.filter_by(status='active')
    if type_filter != 'all':
        query = query.filter_by(type=type_filter)
    
    reports = query.order_by(LostFound.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('lost_found/reports.html', reports=reports, type_filter=type_filter)

@app.route('/lost-found/report', methods=['GET', 'POST'])
@login_required
def report_lost_found():
    if request.method == 'POST':
        print("=" * 50)
        print("POST request received")
        print("Form data:", request.form)
        print("Files:", request.files)
        print("=" * 50)
        
        try:
            # Create report manually without form validation
            report = LostFound(
                type=request.form.get('type'),
                location=request.form.get('location'),
                date_seen=datetime.strptime(request.form.get('date_seen'), '%Y-%m-%dT%H:%M'),
                description=request.form.get('description'),
                dog_name=request.form.get('dog_name'),
                breed=request.form.get('breed'),
                color=request.form.get('color'),
                contact_info=request.form.get('contact_info'),
                reporter_id=current_user.id,
                status='active'
            )
            
            # Handle photo upload
            if 'photo' in request.files:
                photo = request.files['photo']
                if photo and photo.filename:
                    photo_filename = save_file(photo)
                    report.photo = photo_filename
            
            db.session.add(report)
            db.session.commit()
            
            # Notify relevant users based on report type
            if report.type == 'lost':
                notify_all_users(
                    title='Lost Dog Reported',
                    message=f'A dog has been reported lost in {report.location}. Please help spread the word!',
                    type='lost_found',
                    reference_id=report.id
                )
            else:
                # Notify users who have reported lost dogs in similar area
                lost_reports = LostFound.query.filter_by(type='lost', status='active').all()
                for lost_report in lost_reports:
                    create_notification(
                        user_id=lost_report.reporter_id,
                        title='Found Dog Match Possible',
                        message=f'A dog matching your lost report in {report.location} has been found.',
                        type='lost_found',
                        reference_id=report.id
                    )
            
            flash('Report submitted successfully!', 'success')
            return redirect(url_for('lost_found_reports'))
            
        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('report_lost_found'))
    
    # GET request - show form
    form = LostFoundForm()
    return render_template('lost_found/create.html', form=form)

@app.route('/lost-found/<int:report_id>')
def view_report(report_id):
    report = LostFound.query.get_or_404(report_id)
    return render_template('lost_found/details.html', report=report)

@app.route('/lost-found/<int:report_id>/resolve', methods=['POST'])
@login_required
def resolve_report(report_id):
    report = LostFound.query.get_or_404(report_id)
    
    if report.reporter_id != current_user.id and current_user.user_type not in ['shelter', 'vet']:
        abort(403)
    
    report.status = 'resolved'
    db.session.commit()
    
    flash('Report marked as resolved. Thank you for helping!', 'success')
    return redirect(url_for('lost_found_reports'))

@app.route('/quick-add-report')
@login_required
def quick_add_report():
    """Quick way to add a test report"""
    try:
        report = LostFound(
            type='lost',
            dog_name='Quick Test Dog',
            breed='Mixed',
            color='Black',
            location='Quick Add Location',
            date_seen=datetime.now(),
            description='This report was added via quick-add',
            contact_info=current_user.email,
            status='active',
            reporter_id=current_user.id
        )
        
        db.session.add(report)
        db.session.commit()
        
        flash('Test report added successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('lost_found_reports'))

# Educational Module Routes
@app.route('/education')
def education_resources():
    category = request.args.get('category', 'all')
    page = request.args.get('page', 1, type=int)
    
    query = EducationalResource.query
    if category != 'all':
        query = query.filter_by(category=category)
    
    resources = query.order_by(EducationalResource.created_at.desc()).paginate(page=page, per_page=9)
    return render_template('education/resources.html', resources=resources, category=category)

@app.route('/education/<int:resource_id>')
def view_article(resource_id):
    resource = EducationalResource.query.get_or_404(resource_id)
    resource.views += 1
    db.session.commit()
    return render_template('education/article.html', resource=resource)

# Admin routes for educational resources
@app.route('/education/create', methods=['GET', 'POST'])
@login_required
def create_educational_resource():
    if current_user.user_type not in ['shelter', 'vet']:
        flash('Only authorized personnel can create educational resources.', 'warning')
        return redirect(url_for('education_resources'))
    
    form = EducationalResourceForm()
    
    if form.validate_on_submit():
        try:
            # Handle file upload
            media_filename = None
            if form.media_file.data and form.media_file.data.filename:
                media_filename = save_media_file(form.media_file.data)
            
            # Store as plain text - NO HTML, NO MARKDOWN
            resource = EducationalResource(
                title=form.title.data,
                category=form.category.data,
                content=form.content.data,  # Plain text only
                author=form.author.data or current_user.username,
                thumbnail=media_filename
            )
            
            db.session.add(resource)
            db.session.commit()
            
            # Notify all users
            notify_all_users(
                title='New Educational Resource Available',
                message=f'A new article "{form.title.data}" has been published.',
                type='system',
                reference_id=resource.id
            )
            
            flash('Educational resource created successfully!', 'success')
            return redirect(url_for('education_resources'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            flash(f'Error creating resource: {str(e)}', 'danger')
    else:
        if request.method == 'POST':
            print("Form validation failed!")
            print(form.errors)
            flash('Please correct the errors below.', 'danger')
    
    return render_template('education/create.html', form=form)


@app.route('/notifications')
@login_required
def notifications():
    """Display all notifications page"""
    return render_template('notifications.html')


# Optimized Notification API endpoints
@app.route('/api/notifications')
@login_required
def get_notifications():
    """Get unread notifications - optimized for speed"""
    # Limit to 10 most recent unread notifications
    notifications = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).order_by(Notification.created_at.desc()).limit(10).all()
    
    return jsonify({
        'notifications': [n.to_dict() for n in notifications],
        'total': len(notifications)
    })

@app.route('/api/notifications/all')
@login_required
def get_all_notifications():
    """Get all notifications with efficient pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Load only 10 at a time
    
    # Only get last 30 days of notifications
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).filter(
        Notification.created_at >= thirty_days_ago
    ).order_by(Notification.created_at.desc()).paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return jsonify({
        'notifications': [n.to_dict() for n in notifications.items],
        'total': notifications.total,
        'pages': notifications.pages,
        'current_page': notifications.page,
        'has_next': notifications.has_next
    })

@app.route('/api/notifications/count')
@login_required
def get_unread_count():
    """Get unread count - fast COUNT query"""
    count = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).count()
    return jsonify({'count': count})

@app.route('/api/notifications/mark-read', methods=['POST'])
@login_required
def mark_notifications_read():
    """Mark notifications as read"""
    data = request.get_json()
    notification_ids = data.get('notification_ids', [])
    
    if notification_ids:
        # Mark specific notifications as read
        Notification.query.filter(
            Notification.id.in_(notification_ids),
            Notification.user_id == current_user.id
        ).update({'is_read': True}, synchronize_session=False)
    else:
        # Mark all as read
        Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).update({'is_read': True}, synchronize_session=False)
    
    db.session.commit()
    return jsonify({'success': True})

# API endpoints for AJAX calls
@app.route('/api/search')
def search():
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    
    dogs = Dog.query.filter(Dog.name.contains(query)).limit(5).all()
    listings = AdoptionListing.query.filter(AdoptionListing.dog_name.contains(query)).limit(5).all()
    resources = EducationalResource.query.filter(EducationalResource.title.contains(query)).limit(5).all()
    
    results = {
        'dogs': [{'id': d.id, 'name': d.name, 'type': 'dog'} for d in dogs],
        'listings': [{'id': l.id, 'name': l.dog_name, 'type': 'adoption'} for l in listings],
        'resources': [{'id': r.id, 'title': r.title, 'type': 'education'} for r in resources]
    }
    
    return jsonify(results)

@app.route('/api/dashboard/stats')
@login_required
def dashboard_stats():
    stats = {}
    
    if current_user.user_type == 'owner':
        stats['total_dogs'] = Dog.query.filter_by(owner_id=current_user.id).count()
        stats['upcoming_appointments'] = Appointment.query.join(Dog).filter(
            Dog.owner_id == current_user.id,
            Appointment.appointment_date > datetime.now()
        ).count()
        stats['vaccinations_due'] = Vaccination.query.join(Dog).filter(
            Dog.owner_id == current_user.id,
            Vaccination.next_due_date <= datetime.now()
        ).count()
    
    return jsonify(stats)

@app.route('/api/similar-reports')
def similar_reports():
    report_type = request.args.get('type')
    location = request.args.get('location')
    exclude_id = request.args.get('exclude', type=int)
    
    query = LostFound.query.filter_by(type=report_type, status='active')
    if location:
        # Get the first part of location before comma for better matching
        location_part = location.split(',')[0].strip()
        query = query.filter(LostFound.location.contains(location_part))
    if exclude_id:
        query = query.filter(LostFound.id != exclude_id)
    
    reports = query.limit(5).all()
    return jsonify([{
        'id': r.id,
        'dog_name': r.dog_name,
        'location': r.location,
        'type': r.type
    } for r in reports])

@app.route('/api/related-articles')
def related_articles():
    category = request.args.get('category')
    exclude_id = request.args.get('exclude', type=int)
    
    query = EducationalResource.query.filter_by(category=category)
    if exclude_id:
        query = query.filter(EducationalResource.id != exclude_id)
    
    articles = query.limit(4).all()
    return jsonify([{
        'id': a.id,
        'title': a.title,
        'category': a.category,
        'content': a.content[:150] if a.content else ''
    } for a in articles])

@app.route('/api/send-message', methods=['POST'])
@login_required
def send_message():
    report_id = request.form.get('report_id')
    message = request.form.get('message')
    
    # In a real implementation, you would send an email or store the message
    # For now, just return success
    if not message or not report_id:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    # You could store messages in a database table here
    # For demonstration, we'll just log it
    app.logger.info(f"Message from {current_user.username} about report {report_id}: {message}")
    
    return jsonify({'success': True})

@app.route('/api/track-reading', methods=['POST'])
def track_reading():
    article_id = request.form.get('article_id')
    time_spent = request.form.get('time_spent')
    
    if article_id:
        # Track reading time for analytics
        # You could store this in a database table for analytics
        app.logger.info(f"Article {article_id} read for {time_spent} seconds")
    
    return jsonify({'success': True})

@app.route('/debug-templates')
def debug_templates():
    import os
    template_dir = os.path.join(app.root_path, 'templates')
    adoption_dir = os.path.join(template_dir, 'adoption')
    
    # Get all template files
    template_files = {}
    for root, dirs, files in os.walk(template_dir):
        rel_path = os.path.relpath(root, template_dir)
        if rel_path == '.':
            rel_path = 'root'
        template_files[rel_path] = files
    
    debug_info = {
        'template_folder': app.template_folder,
        'root_path': app.root_path,
        'template_dir_exists': os.path.exists(template_dir),
        'adoption_dir_exists': os.path.exists(adoption_dir),
        'files_in_adoption': os.listdir(adoption_dir) if os.path.exists(adoption_dir) else [],
        'all_template_files': template_files,
        'current_working_directory': os.getcwd()
    }
    return jsonify(debug_info)

@app.route('/add-sample-data')
def add_sample_data():
    """Add sample lost/found reports for testing"""
    try:
        # Check if there are any reports
        if LostFound.query.count() > 0:
            return jsonify({'message': f'Already have {LostFound.query.count()} reports in database'})
        
        # Get or create a test user
        user = User.query.first()
        if not user:
            return jsonify({'error': 'No users found. Please register a user first.'}), 400
        
        # Sample lost reports
        sample_reports = [
            LostFound(
                type='lost',
                dog_name='Max',
                breed='Golden Retriever',
                color='Golden',
                location='Central Park',
                date_seen=datetime.now(),
                description='Friendly golden retriever, wearing a blue collar, responds to "Max"',
                contact_info='555-0101',
                status='active',
                reporter_id=user.id
            ),
            LostFound(
                type='lost',
                dog_name='Luna',
                breed='Husky',
                color='White and grey',
                location='Riverdale Area',
                date_seen=datetime.now(),
                description='Husky with blue eyes, very energetic',
                contact_info='555-0102',
                status='active',
                reporter_id=user.id
            ),
            LostFound(
                type='found',
                dog_name='Charlie',
                breed='Beagle',
                color='Brown and white',
                location='Community Park',
                date_seen=datetime.now(),
                description='Found near the playground, wearing a red collar',
                contact_info='555-0103',
                status='active',
                reporter_id=user.id
            ),
            LostFound(
                type='found',
                dog_name='Coco',
                breed='Poodle Mix',
                color='White',
                location='Main Street',
                date_seen=datetime.now(),
                description='Small poodle mix, very friendly',
                contact_info='555-0104',
                status='active',
                reporter_id=user.id
            )
        ]
        
        db.session.add_all(sample_reports)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Added {len(sample_reports)} sample lost/found reports',
            'total_reports': LostFound.query.count()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/debug-form', methods=['GET', 'POST'])
@login_required
def debug_form():
    if request.method == 'POST':
        print("POST data:", request.form)
        print("FILES:", request.files)
        return jsonify({
            'message': 'Form received',
            'data': dict(request.form),
            'files': [f for f in request.files]
        })
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Debug Form</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <h2>Debug Form</h2>
            <form method="POST" enctype="multipart/form-data">
                <div class="mb-3">
                    <label>Type</label>
                    <select name="type" class="form-control">
                        <option value="lost">Lost</option>
                        <option value="found">Found</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label>Location</label>
                    <input type="text" name="location" class="form-control" required>
                </div>
                <div class="mb-3">
                    <label>Date Seen</label>
                    <input type="datetime-local" name="date_seen" class="form-control" required>
                </div>
                <div class="mb-3">
                    <label>Description</label>
                    <textarea name="description" class="form-control" required></textarea>
                </div>
                <button type="submit" class="btn btn-primary">Submit</button>
            </form>
        </div>
        <script>
            const now = new Date();
            now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
            document.querySelector('input[type="datetime-local"]').value = now.toISOString().slice(0, 16);
        </script>
    </body>
    </html>
    '''

# Create database tables
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")
    print(f"Template directory: {app.template_folder}")
    print(f"Static directory: {app.static_folder}")

@app.route('/api/pending-requests-count')
@login_required
def pending_requests_count():
    if current_user.user_type != 'shelter':
        return jsonify({'count': 0})
    
    count = ApprovalRequest.query.filter_by(status='pending').count()
    return jsonify({'count': count})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)