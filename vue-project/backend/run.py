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

    # Ensure any newly introduced tables (e.g. password_reset_codes) are created
    db.create_all()

with app.app_context():
    ensure_schema()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
