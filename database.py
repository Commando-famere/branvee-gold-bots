"""
Database handler for SQLite
"""
import sqlite3
from datetime import datetime, timedelta
from config import DB_PATH

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables"""
    conn = get_db()
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        token TEXT UNIQUE NOT NULL,
        telegram_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP NOT NULL,
        last_renewed TIMESTAMP,
        renewed_count INTEGER DEFAULT 0,
        is_active BOOLEAN DEFAULT 1,
        is_suspended BOOLEAN DEFAULT 0,
        notes TEXT,
        created_by INTEGER
    )''')
    
    # Renewal history table
    c.execute('''CREATE TABLE IF NOT EXISTS renewal_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        old_expiry TIMESTAMP,
        new_expiry TIMESTAMP,
        renewed_by INTEGER,
        renewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        reason TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

def add_user(email, token, expires_at, created_by):
    """Add new user to database"""
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO users (email, token, expires_at, created_by)
            VALUES (?, ?, ?, ?)
        ''', (email, token, expires_at, created_by))
        conn.commit()
        user_id = c.lastrowid
        return user_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_user_by_email(email):
    """Get user by email"""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = c.fetchone()
    conn.close()
    return user

def get_user_by_token(token):
    """Get user by token"""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE token = ?', (token,))
    user = c.fetchone()
    conn.close()
    return user

def get_all_users():
    """Get all users"""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users ORDER BY created_at DESC')
    users = c.fetchall()
    conn.close()
    return users

def get_active_users():
    """Get active users (not expired, not suspended)"""
    conn = get_db()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute('''
        SELECT * FROM users 
        WHERE expires_at > ? AND is_active = 1 AND is_suspended = 0
        ORDER BY created_at DESC
    ''', (now,))
    users = c.fetchall()
    conn.close()
    return users

def get_expired_users():
    """Get expired users"""
    conn = get_db()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute('''
        SELECT * FROM users 
        WHERE expires_at <= ?
        ORDER BY created_at DESC
    ''', (now,))
    users = c.fetchall()
    conn.close()
    return users

def renew_user(user_id, new_expiry, renewed_by):
    """Renew user access"""
    conn = get_db()
    c = conn.cursor()
    
    # Get old expiry
    c.execute('SELECT expires_at FROM users WHERE id = ?', (user_id,))
    old = c.fetchone()
    
    if not old:
        conn.close()
        return False
    
    old_expiry = old['expires_at']
    
    # Update user
    c.execute('''
        UPDATE users 
        SET expires_at = ?, last_renewed = ?, renewed_count = renewed_count + 1
        WHERE id = ?
    ''', (new_expiry, datetime.now().isoformat(), user_id))
    
    # Log renewal
    c.execute('''
        INSERT INTO renewal_history (user_id, old_expiry, new_expiry, renewed_by)
        VALUES (?, ?, ?, ?)
    ''', (user_id, old_expiry, new_expiry, renewed_by))
    
    conn.commit()
    conn.close()
    return True

def suspend_user(user_id):
    """Suspend user access"""
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE users SET is_suspended = 1 WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return True

def activate_user(user_id):
    """Activate suspended user"""
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE users SET is_suspended = 0 WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return True

def delete_user(user_id):
    """Delete user (soft delete - set inactive)"""
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE users SET is_active = 0 WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return True

def get_stats():
    """Get user statistics"""
    conn = get_db()
    c = conn.cursor()
    now = datetime.now().isoformat()
    
    total = c.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    active = c.execute('SELECT COUNT(*) FROM users WHERE expires_at > ? AND is_active = 1 AND is_suspended = 0', (now,)).fetchone()[0]
    expired = c.execute('SELECT COUNT(*) FROM users WHERE expires_at <= ?', (now,)).fetchone()[0]
    suspended = c.execute('SELECT COUNT(*) FROM users WHERE is_suspended = 1').fetchone()[0]
    
    conn.close()
    return {
        "total": total,
        "active": active,
        "expired": expired,
        "suspended": suspended
    }

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def get_user_by_email(email):
    """Get user by email"""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = c.fetchone()
    conn.close()
    return user
