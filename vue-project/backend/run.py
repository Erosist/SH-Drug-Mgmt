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
    # Check columns for 'role'
    columns = [c['name'] for c in inspector.get_columns('users')]
    if 'role' not in columns:
        # SQLite supports simple ALTER TABLE ADD COLUMN
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'unauth'"))
        print('[schema] Added role column to users table')

with app.app_context():
    ensure_schema()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
