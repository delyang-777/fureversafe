import os
import time
from app import app, db
from models import User, ApprovalRequest
from datetime import datetime

def force_reset_database():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'fureversafe.db')
    
    # Try to close any existing connections
    try:
        with app.app_context():
            db.session.remove()
            db.engine.dispose()
    except:
        pass
    
    # Wait a moment for connections to close
    time.sleep(1)
    
    # Try to delete the database file
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("✅ Deleted old database")
        except PermissionError:
            print("⚠️ Could not delete database file. Trying alternative method...")
            # Rename instead of delete
            backup_path = db_path + ".old"
            os.rename(db_path, backup_path)
            print(f"✅ Renamed old database to {backup_path}")
    
    # Create new database
    with app.app_context():
        db.create_all()
        print("✅ Created new database with approval columns")
        
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
        db.session.flush()
        
        # Create approved vet
        vet = User(
            username='test_vet',
            email='vet@example.com',
            user_type='vet',
            is_approved=True,
            approved_by=shelter.id,
            approved_at=datetime.now()
        )
        vet.set_password('vet123')
        db.session.add(vet)
        
        # Create approved owner
        owner = User(
            username='test_owner',
            email='owner@example.com',
            user_type='owner',
            is_approved=True,
            approved_by=shelter.id,
            approved_at=datetime.now()
        )
        owner.set_password('owner123')
        db.session.add(owner)
        
        # Create pending user
        pending = User(
            username='pending_user',
            email='pending@example.com',
            user_type='owner',
            is_approved=False
        )
        pending.set_password('pending123')
        db.session.add(pending)
        db.session.flush()
        
        # Create approval request
        approval_request = ApprovalRequest(
            user_id=pending.id,
            requested_by=pending.id,
            user_type_requested='owner',
            reason='I want to join the platform to help dogs find homes.',
            status='pending'
        )
        db.session.add(approval_request)
        
        db.session.commit()
        
        print("\n" + "="*50)
        print("✅ Database reset complete!")
        print("="*50)
        print("\n📋 LOGIN CREDENTIALS:")
        print("-" * 30)
        print("\n🏢 SHELTER (Admin):")
        print("   Username: admin_shelter")
        print("   Password: shelter123")
        print("   Email: shelter@example.com")
        print("\n🏥 VETERINARIAN:")
        print("   Username: test_vet")
        print("   Password: vet123")
        print("\n🐕 DOG OWNER:")
        print("   Username: test_owner")
        print("   Password: owner123")
        print("\n⏳ PENDING USER:")
        print("   Username: pending_user")
        print("   Password: pending123")
        print("\n" + "="*50)

if __name__ == "__main__":
    force_reset_database()