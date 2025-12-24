#!/usr/bin/env python3
from models import User
from extensions import db
from app import app

app.app_context().push()
users = User.query.all()
print("Users in database:")
for u in users:
    print(f"  - {u.username} ({u.role})")
