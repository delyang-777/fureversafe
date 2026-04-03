from app import app, db
from models import User
from datetime import datetime

with app.app_context():
    # Create admin shelter with auto-approve capability
    admin = User.query.filter_by(email='admin@fureversafe.com').first()
    
    if not admin:
        admin = User(
            username='admin',
            email='admin@fureversafe.com',
            user_type='shelter',
            is_approved=True,
            approved_at=datetime.now()
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin created!")
        print("Email: admin@fureversafe.com")
        print("Password: admin123")
    else:
        print("Admin already exists")