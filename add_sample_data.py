from app import app, db
from models import LostFound, User
from datetime import datetime

with app.app_context():
    # Get first user
    user = User.query.first()
    
    if not user:
        print("❌ No user found. Please register a user first via the web interface.")
        print("   Go to: http://localhost:5000/register")
    else:
        # Check existing reports
        existing = LostFound.query.count()
        print(f"Existing reports: {existing}")
        
        if existing == 0:
            # Add sample reports
            reports = [
                LostFound(
                    type='lost',
                    dog_name='Max',
                    breed='Golden Retriever',
                    color='Golden',
                    location='Central Park',
                    date_seen=datetime.now(),
                    description='Friendly golden retriever, wearing a blue collar',
                    contact_info='555-0101',
                    status='active',
                    reporter_id=user.id
                ),
                LostFound(
                    type='lost',
                    dog_name='Luna',
                    breed='Husky',
                    color='White and grey',
                    location='Riverdale',
                    date_seen=datetime.now(),
                    description='Husky with blue eyes',
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
                    description='Found near playground',
                    contact_info='555-0103',
                    status='active',
                    reporter_id=user.id
                )
            ]
            
            db.session.add_all(reports)
            db.session.commit()
            print(f"✅ Added {len(reports)} sample reports!")
        else:
            print(f"✅ Already have {existing} reports in database")
        
        # Show current reports
        all_reports = LostFound.query.all()
        print(f"\nCurrent reports in database ({len(all_reports)}):")
        for r in all_reports:
            print(f"  - {r.type}: {r.dog_name} at {r.location}")