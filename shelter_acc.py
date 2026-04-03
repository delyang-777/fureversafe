# setup_database.py
from app import app, db
from models import User, ApprovalRequest
from datetime import datetime
import os

def setup_database():
    print("=" * 50)
    print("Setting up FurEverSafe Database")
    print("=" * 50)
    
    with app.app_context():
        # Delete existing database
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'fureversafe.db')
        if os.path.exists(db_path):
            os.remove(db_path)
            print("✅ Deleted existing database")
        
        # Create all tables
        db.create_all()
        print("✅ Created all tables with new schema")
        
        # Create shelter account
        shelter = User(
            username='admin_shelter',
            email='shelter@example.com',
            user_type='shelter',
            is_approved=True,
            approved_at=datetime.now()
        )
        shelter.set_password('shelter123')
        db.session.add(shelter)
        
        # Create a test vet account (approved)
        vet = User(
            username='test_vet',
            email='vet@example.com',
            user_type='vet',
            is_approved=True,
            approved_by=shelter.id if shelter.id else None,
            approved_at=datetime.now()
        )
        vet.set_password('vet123')
        db.session.add(vet)
        
        # Create a test owner account (approved)
        owner = User(
            username='test_owner',
            email='owner@example.com',
            user_type='owner',
            is_approved=True,
            approved_by=shelter.id if shelter.id else None,
            approved_at=datetime.now()
        )
        owner.set_password('owner123')
        db.session.add(owner)
        
        # Create a pending approval request
        pending_user = User(
            username='pending_user',
            email='pending@example.com',
            user_type='owner',
            is_approved=False
        )
        pending_user.set_password('pending123')
        db.session.add(pending_user)
        
        db.session.flush()  # Get IDs
        
        # Create approval request for pending user
        approval_request = ApprovalRequest(
            user_id=pending_user.id,
            requested_by=pending_user.id,
            user_type_requested='owner',
            reason='I want to join the platform to manage my dogs and help with animal welfare.',
            status='pending'
        )
        db.session.add(approval_request)
        
        db.session.commit()
        
        print("\n✅ Database setup complete!")
        print("\n" + "=" * 50)
        print("Created Accounts:")
        print("=" * 50)
        print("\n🔐 Shelter Account (Admin):")
        print("   Username: admin_shelter")
        print("   Password: shelter123")
        print("   Email: shelter@example.com")
        print("   Role: Can approve/reject user registrations")
        
        print("\n🏥 Veterinarian Account:")
        print("   Username: test_vet")
        print("   Password: vet123")
        print("   Email: vet@example.com")
        
        print("\n🐕 Dog Owner Account:")
        print("   Username: test_owner")
        print("   Password: owner123")
        print("   Email: owner@example.com")
        
        print("\n⏳ Pending User (Needs Approval):")
        print("   Username: pending_user")
        print("   Password: pending123")
        print("   Email: pending@example.com")
        print("   Status: Pending Approval")
        
        print("\n" + "=" * 50)
        print("Next Steps:")
        print("=" * 50)
        print("1. Run: python app.py")
        print("2. Login as shelter: admin_shelter / shelter123")
        print("3. Go to: http://localhost:5000/approval-dashboard")
        print("4. Approve or reject pending users")
        print("5. Test login with approved users")

if __name__ == "__main__":
    setup_database()