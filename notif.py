from app import app, db
from models import Notification

with app.app_context():
    # Create indexes for faster queries
    from sqlalchemy import Index
    try:
        Index('idx_notification_user_read', Notification.user_id, Notification.is_read).create(db.engine)
        print("✅ Added index on user_id and is_read")
    except:
        print("Index already exists")
    
    try:
        Index('idx_notification_created', Notification.created_at).create(db.engine)
        print("✅ Added index on created_at")
    except:
        print("Index already exists")