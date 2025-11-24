from app import create_app
from extensions import db
from sqlalchemy import inspect, text

app = create_app()

def ensure_schema():
    """Create tables if missing; add role column if upgrading existing SQLite schema."""
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    if 'users' not in tables:
        db.create_all()
        return

    columns = [c['name'] for c in inspector.get_columns('users')]
    with db.engine.connect() as conn:
        if 'role' not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'unauth'"))
            print('[schema] Added role column to users table')
        if 'phone' not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR(30)"))
            conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_phone ON users(phone)"))
            print('[schema] Added phone column to users table')
        if 'real_name' not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN real_name VARCHAR(120)"))
            print('[schema] Added real_name column to users table')
        if 'company_name' not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN company_name VARCHAR(160)"))
            print('[schema] Added company_name column to users table')
        if 'is_active' not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 1"))
            print('[schema] Added is_active column to users table')
        if 'last_login_at' not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN last_login_at DATETIME"))
            print('[schema] Added last_login_at column to users table')
        if 'enterprise_certifications' in tables:
            cert_cols = [c['name'] for c in inspector.get_columns('enterprise_certifications')]
            if 'reviewer_id' not in cert_cols:
                conn.execute(text("ALTER TABLE enterprise_certifications ADD COLUMN reviewer_id INTEGER"))
                print('[schema] Added reviewer_id column to enterprise_certifications')

    # Ensure any newly introduced tables are created
    db.create_all()

with app.app_context():
    ensure_schema()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
