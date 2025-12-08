"""
Script to create the first admin user
"""
from database import Database
from auth import hash_password

def create_admin():
    """Create admin user"""
    db = Database()
    
    print("="*60)
    print("Create Admin User")
    print("="*60)
    
    email = input("Enter admin email: ").strip()
    password = input("Enter admin password: ").strip()
    name = input("Enter admin name: ").strip()
    
    if not email or not password or not name:
        print("Error: All fields are required")
        return
    
    try:
        # Check if user exists
        existing_user = db.get_user_by_email(email)
        if existing_user:
            print(f"Error: User with email {email} already exists")
            return
        
        # Check if any admin exists
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE role = ?', ('admin',))
        if cursor.fetchone():
            print("Error: Admin user already exists. Only one admin is allowed.")
            conn.close()
            return
        conn.close()
        
        # Create admin
        password_hash = hash_password(password)
        user_id = db.create_user(email, password_hash, name, 'admin')
        
        print(f"\n✓ Admin user created successfully!")
        print(f"  Email: {email}")
        print(f"  Name: {name}")
        print(f"  User ID: {user_id}")
        print("\nYou can now login with these credentials.")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    create_admin()

