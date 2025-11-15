from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


def to_iso(value):
    if not value:
        return None
    try:
        return value.isoformat()
    except AttributeError:
        return str(value)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(30), unique=True, nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='unauth')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'created_at': self.created_at.isoformat()
        }


class PasswordResetCode(db.Model):
    __tablename__ = 'password_reset_codes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    channel = db.Column(db.String(10), nullable=False)  # email / phone
    contact_value = db.Column(db.String(120), nullable=False)
    code_hash = db.Column(db.String(128), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('reset_codes', lazy=True))

    def verify_code(self, code: str) -> bool:
        return check_password_hash(self.code_hash, code)


class Drug(db.Model):
    __tablename__ = 'drugs'

    id = db.Column(db.Integer, primary_key=True)
    generic_name = db.Column(db.String(120), nullable=False)
    brand_name = db.Column(db.String(120), nullable=False)
    approval_number = db.Column(db.String(50), unique=True, nullable=False)
    dosage_form = db.Column(db.String(80), nullable=False)
    specification = db.Column(db.String(80), nullable=False)
    manufacturer = db.Column(db.String(160), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    prescription_type = db.Column(db.String(40), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    inventory_items = db.relationship('InventoryItem', backref='drug', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'generic_name': self.generic_name,
            'brand_name': self.brand_name,
            'approval_number': self.approval_number,
            'dosage_form': self.dosage_form,
            'specification': self.specification,
            'manufacturer': self.manufacturer,
            'category': self.category,
            'prescription_type': self.prescription_type,
            'created_at': to_iso(self.created_at),
            'updated_at': to_iso(self.updated_at),
        }


class TenantPharmacy(db.Model):
    __tablename__ = 'tenants_pharmacy'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    type = db.Column(db.String(40), nullable=False)
    unified_social_credit_code = db.Column(db.String(40), unique=True, nullable=False)
    legal_representative = db.Column(db.String(60), nullable=False)
    contact_person = db.Column(db.String(60), nullable=False)
    contact_phone = db.Column(db.String(40), nullable=False)
    contact_email = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    business_scope = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    inventory_items = db.relationship('InventoryItem', backref='tenant', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'unified_social_credit_code': self.unified_social_credit_code,
            'legal_representative': self.legal_representative,
            'contact_person': self.contact_person,
            'contact_phone': self.contact_phone,
            'contact_email': self.contact_email,
            'address': self.address,
            'business_scope': self.business_scope,
            'is_active': self.is_active,
            'created_at': to_iso(self.created_at),
            'updated_at': to_iso(self.updated_at),
        }


class InventoryItem(db.Model):
    __tablename__ = 'inventory_items'

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants_pharmacy.id'), nullable=False)
    drug_id = db.Column(db.Integer, db.ForeignKey('drugs.id'), nullable=False)
    batch_number = db.Column(db.String(60), nullable=False)
    production_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    def to_dict(self, include_related: bool = False):
        data = {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'drug_id': self.drug_id,
            'batch_number': self.batch_number,
            'production_date': to_iso(self.production_date),
            'expiry_date': to_iso(self.expiry_date),
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'created_at': to_iso(self.created_at),
            'updated_at': to_iso(self.updated_at),
        }
        if include_related:
            if self.drug:
                data['drug_name'] = self.drug.generic_name
                data['drug_brand'] = self.drug.brand_name
                data['prescription_type'] = self.drug.prescription_type
            if self.tenant:
                data['tenant_name'] = self.tenant.name
                data['tenant_type'] = self.tenant.type
        return data
