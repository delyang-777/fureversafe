from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, IntegerField, FloatField, SelectField, DateTimeField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
from datetime import datetime

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    user_type = SelectField('Account Type', choices=[
        ('owner', 'Dog Owner'), 
        ('vet', 'Veterinarian')
    ])  # Removed shelter option - shelters are created separately
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    organization_name = StringField('Organization/Shelter Name (for approval)')
    reason = TextAreaField('Reason for joining', validators=[DataRequired()])
    submit = SubmitField('Request Approval')
    
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class DogProfileForm(FlaskForm):
    name = StringField('Dog Name', validators=[DataRequired()])
    breed = StringField('Breed', validators=[DataRequired()])
    age = IntegerField('Age (years)')
    weight = FloatField('Weight (kg)')
    microchip_id = StringField('Microchip ID')
    photo = FileField('Dog Photo', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    submit = SubmitField('Save Dog Profile')

class VaccinationForm(FlaskForm):
    vaccine_name = StringField('Vaccine Name', validators=[DataRequired()])
    date_administered = DateTimeField('Date Administered', format='%Y-%m-%d %H:%M', default=datetime.now)
    next_due_date = DateTimeField('Next Due Date', format='%Y-%m-%d %H:%M')
    administered_by = StringField('Administered By')
    submit = SubmitField('Add Vaccination')

class AppointmentForm(FlaskForm):
    appointment_type = StringField('Appointment Type', validators=[DataRequired()])
    appointment_date = DateTimeField('Appointment Date', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    vet_name = StringField('Veterinarian Name')
    location = StringField('Location')
    notes = TextAreaField('Notes')
    submit = SubmitField('Schedule Appointment')

class HealthRecordForm(FlaskForm):
    record_type = StringField('Record Type', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    date = DateTimeField('Date', format='%Y-%m-%d %H:%M', default=datetime.now)
    vet_name = StringField('Veterinarian Name')
    notes = TextAreaField('Additional Notes')
    submit = SubmitField('Add Health Record')

class AdoptionListingForm(FlaskForm):
    dog_name = StringField('Dog Name', validators=[DataRequired()])
    breed = StringField('Breed', validators=[DataRequired()])
    age = IntegerField('Age (years)')
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female')])
    size = SelectField('Size', choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')])
    description = TextAreaField('Description', validators=[DataRequired()])
    photo = FileField('Dog Photo', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    submit = SubmitField('Create Listing')

class AdoptionApplicationForm(FlaskForm):
    message = TextAreaField('Message to Shelter', validators=[DataRequired()])
    submit = SubmitField('Submit Application')

class LostFoundForm(FlaskForm):
    type = SelectField('Report Type', choices=[('lost', 'Lost Dog'), ('found', 'Found Dog')], validators=[DataRequired()])
    dog_name = StringField('Dog Name (if known)')
    breed = StringField('Breed')
    color = StringField('Color/Markings')
    location = StringField('Location', validators=[DataRequired()])
    date_seen = DateTimeField('Date Seen', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    contact_info = StringField('Contact Information')
    photo = FileField('Photo', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    submit = SubmitField('Submit Report')

class EducationalResourceForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    category = SelectField('Category', choices=[('training', 'Training'), ('health', 'Health'), ('nutrition', 'Nutrition'), ('welfare', 'Animal Welfare')])
    content = TextAreaField('Content', validators=[DataRequired()])
    author = StringField('Author')
    thumbnail = FileField('Thumbnail', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    submit = SubmitField('Publish Resource')