import os
import sys

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database import engine, Base, SessionLocal
from models import User, BusinessProfile
from services.auth_service import get_password_hash
from services.ingestion_service import seed_database_from_excel

def init_db():
    print("Creating all database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

    db = SessionLocal()
    try:
        # Check if default admin exists
        admin = db.query(User).filter(User.email == "admin@retailbi.com").first()
        if not admin:
            print("Creating default admin user (admin@retailbi.com)...")
            admin = User(
                email="admin@retailbi.com",
                hashed_password=get_password_hash("Admin@123456"),
                full_name="System Administrator",
                role="admin",
                is_active=True
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)

            # Create admin business profile
            profile = BusinessProfile(
                user_id=admin.id,
                company_name="Apex Retail Global",
                industry="Retail",
                team_size="50-100",
                target_margin=25.00,
                business_goals="Drive gross profit margin to 25%, minimize digital return leakage, and eliminate stockouts on key inventory."
            )
            db.add(profile)
            db.commit()

        # Check if default manager exists
        manager = db.query(User).filter(User.email == "manager@retailbi.com").first()
        if not manager:
            print("Creating default manager user (manager@retailbi.com)...")
            manager = User(
                email="manager@retailbi.com",
                hashed_password=get_password_hash("Manager@123456"),
                full_name="Operations Manager",
                role="manager",
                is_active=True
            )
            db.add(manager)
            db.commit()
            db.refresh(manager)

            profile = BusinessProfile(
                user_id=manager.id,
                company_name="Apex Retail Global",
                industry="Retail",
                team_size="50-100",
                target_margin=25.00,
                business_goals="Optimize store replenishment, manage discount elasticity, and review strategic AI recommendations."
            )
            db.add(profile)
            db.commit()

        # Seed data from Excel
        print("Seeding retail business records from 03_Retail.xlsx...")
        result = seed_database_from_excel(db)
        print(f"Seed result: {result}")
        print("Database initialization complete!")

    finally:
        db.close()

if __name__ == "__main__":
    init_db()
