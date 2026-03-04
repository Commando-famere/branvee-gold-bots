import sqlite3

try:
    conn = sqlite3.connect('branvee.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Check if users table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    if not c.fetchone():
        print("❌ Users table does not exist!")
    else:
        print("✅ Users table exists")
        
        # Count users
        c.execute("SELECT COUNT(*) FROM users;")
        count = c.fetchone()[0]
        print(f"📊 Total users: {count}")
        
        # List all users
        if count > 0:
            c.execute("SELECT id, email, token, expires_at, is_suspended FROM users;")
            users = c.fetchall()
            for user in users:
                print(f"\n📧 ID: {user[0]}")
                print(f"   Email: {user[1]}")
                print(f"   Token: {user[2]}")
                print(f"   Expires: {user[3]}")
                print(f"   Suspended: {user[4]}")
        else:
            print("❌ No users found in database")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
