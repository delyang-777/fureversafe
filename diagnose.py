from app import app, db
from models import LostFound, User
from flask_login import current_user

with app.app_context():
    print("=== DIAGNOSTIC REPORT ===")
    
    # Check database
    print(f"\n1. Database file location: {db.engine.url}")
    
    # Check tables
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"\n2. Tables in database: {tables}")
    
    # Check LostFound table columns
    if 'lost_found' in tables:
        columns = inspector.get_columns('lost_found')
        print(f"\n3. LostFound table columns:")
        for col in columns:
            print(f"   - {col['name']}: {col['type']}")
    
    # Check users
    users = User.query.all()
    print(f"\n4. Users: {len(users)}")
    for user in users:
        print(f"   - ID: {user.id}, Username: {user.username}")
    
    # Check reports
    reports = LostFound.query.all()
    print(f"\n5. Reports: {len(reports)}")
    
    print("\n=== END DIAGNOSTIC ===")