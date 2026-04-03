from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    user_type = db.Column(db.String(50), default='owner')  # owner, shelter, vet
    is_approved = db.Column(db.Boolean, default=False)  # New field for approval
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Who approved
    approved_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    dogs = db.relationship('Dog', backref='owner', lazy=True)
    adoption_applications = db.relationship('AdoptionApplication', backref='applicant', lazy=True)
    lost_found_reports = db.relationship('LostFound', backref='reporter', lazy=True)
    approved_by_user = db.relationship('User', remote_side=[id], backref='approved_users')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class ApprovalRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    requested_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, approved, rejected
    user_type_requested = db.Column(db.String(50))  # owner, vet
    reason = db.Column(db.Text)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='approval_requests')
    requester = db.relationship('User', foreign_keys=[requested_by], backref='sent_approvals')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by], backref='reviewed_approvals')
    
class Dog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    breed = db.Column(db.String(100))
    age = db.Column(db.Integer)
    weight = db.Column(db.Float)
    microchip_id = db.Column(db.String(50), unique=True)
    photo = db.Column(db.String(200))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    health_records = db.relationship('HealthRecord', backref='dog', lazy=True, cascade='all, delete-orphan')
    vaccinations = db.relationship('Vaccination', backref='dog', lazy=True, cascade='all, delete-orphan')
    appointments = db.relationship('Appointment', backref='dog', lazy=True, cascade='all, delete-orphan')

class HealthRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dog_id = db.Column(db.Integer, db.ForeignKey('dog.id'), nullable=False)
    record_type = db.Column(db.String(100))  # checkup, surgery, etc.
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    vet_name = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Vaccination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dog_id = db.Column(db.Integer, db.ForeignKey('dog.id'), nullable=False)
    vaccine_name = db.Column(db.String(100), nullable=False)
    date_administered = db.Column(db.DateTime, nullable=False)
    next_due_date = db.Column(db.DateTime)
    administered_by = db.Column(db.String(100))
    certificate = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dog_id = db.Column(db.Integer, db.ForeignKey('dog.id'), nullable=False)
    appointment_type = db.Column(db.String(100), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    vet_name = db.Column(db.String(100))
    location = db.Column(db.String(200))
    notes = db.Column(db.Text)
    reminder_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AdoptionListing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shelter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    dog_name = db.Column(db.String(100), nullable=False)
    breed = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    size = db.Column(db.String(50))
    description = db.Column(db.Text)
    photo = db.Column(db.String(200))
    status = db.Column(db.String(50), default='available')  # available, pending, adopted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    applications = db.relationship('AdoptionApplication', backref='listing', lazy=True, cascade='all, delete-orphan')

class AdoptionApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('adoption_listing.id'), nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, approved, rejected
    message = db.Column(db.Text)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)

class LostFound(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)  # lost, found
    dog_name = db.Column(db.String(100))
    breed = db.Column(db.String(100))
    color = db.Column(db.String(100))
    location = db.Column(db.String(200), nullable=False)
    date_seen = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text)
    photo = db.Column(db.String(200))
    contact_info = db.Column(db.String(200))
    status = db.Column(db.String(50), default='active')  # active, resolved
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class EducationalResource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))  # training, health, nutrition, welfare
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100))
    thumbnail = db.Column(db.String(200))
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50))  # approval, adoption, lost_found, appointment, system
    reference_id = db.Column(db.Integer)  # ID of related item (adoption_id, report_id, etc.)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='notifications')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'reference_id': self.reference_id,
            'is_read': self.is_read,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }