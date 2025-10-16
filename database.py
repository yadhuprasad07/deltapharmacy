from app import app, db, User, Medicine
from datetime import date, timedelta

def create_database():
    """Creates the database and tables."""
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()
        print("Tables created successfully.")

        # Optional: Add a default user for testing
        if not User.query.filter_by(username='admin').first():
            print("Creating default admin user...")
            admin_user = User(username='admin')
            admin_user.set_password('password')
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created with username 'admin' and password 'password'.")

            # Optional: Add some sample medicines
            print("Adding sample medicines...")
            medicines = [
                Medicine(name='Paracetamol', manufacturer='Cipla', expiry_date=date.today() + timedelta(days=365), quantity=100, price=10.50, added_by=admin_user.id),
                Medicine(name='Aspirin', manufacturer='Bayer', expiry_date=date.today() + timedelta(days=730), quantity=50, price=25.00, added_by=admin_user.id),
                Medicine(name='Ibuprofen', manufacturer='Dr. Reddy\'s', expiry_date=date.today() - timedelta(days=30), quantity=20, price=15.75, added_by=admin_user.id)
            ]
            db.session.bulk_save_objects(medicines)
            db.session.commit()
            print("Sample medicines added.")


if __name__ == '__main__':
    create_database()
