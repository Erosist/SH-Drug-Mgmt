#!/usr/bin/env python3
from models import User
from extensions import db
from app import app

app.app_context().push()

# 重置sfexpress密码
user = User.query.filter_by(username='sfexpress').first()
if user:
    user.set_password('Test123456')
    db.session.commit()
    print(f"Password reset for {user.username}")
else:
    print("User sfexpress not found")

# 也重置admin密码
admin = User.query.filter_by(username='admin').first()
if admin:
    admin.set_password('AdminPass123!')
    db.session.commit()
    print(f"Password reset for {admin.username}")
