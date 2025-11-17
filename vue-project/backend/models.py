from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class Tenant(db.Model):
    """企业租户模型"""
    __tablename__ = 'tenants'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # PHARMACY, SUPPLIER, LOGISTICS, REGULATOR
    unified_social_credit_code = db.Column(db.String(18), unique=True)
    legal_representative = db.Column(db.String(50))
    contact_person = db.Column(db.String(50))
    contact_phone = db.Column(db.String(20))
    contact_email = db.Column(db.String(100))
    address = db.Column(db.Text)
    business_scope = db.Column(db.Text)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Drug(db.Model):
    """药品主数据模型"""
    __tablename__ = 'drugs'
    
    id = db.Column(db.Integer, primary_key=True)
    generic_name = db.Column(db.String(100), nullable=False)
    brand_name = db.Column(db.String(100))
    approval_number = db.Column(db.String(50), unique=True)
    dosage_form = db.Column(db.String(50))
    specification = db.Column(db.String(100))
    manufacturer = db.Column(db.String(100))
    category = db.Column(db.String(50))
    prescription_type = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class SupplyInfo(db.Model):
    """供应信息模型"""
    __tablename__ = 'supply_info'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    drug_id = db.Column(db.Integer, db.ForeignKey('drugs.id'), nullable=False, index=True)
    available_quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    valid_until = db.Column(db.Date, nullable=False)
    min_order_quantity = db.Column(db.Integer, nullable=False, default=1)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='ACTIVE')  # ACTIVE, INACTIVE, EXPIRED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    tenant = db.relationship('Tenant', backref='supply_infos')
    drug = db.relationship('Drug', backref='supply_infos')

    def to_dict(self, include_relations=False):
        result = {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'drug_id': self.drug_id,
            'available_quantity': self.available_quantity,
            'unit_price': float(self.unit_price) if self.unit_price else None,
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'min_order_quantity': self.min_order_quantity,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_relations:
            result.update({
                'tenant': self.tenant.to_dict() if self.tenant else None,
                'drug': self.drug.to_dict() if self.drug else None
            })
        
        return result


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(30), unique=True, nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='unauth')
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True, index=True)
    is_authenticated = db.Column(db.Boolean, nullable=False, default=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    last_login_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    tenant = db.relationship('Tenant', backref='users')

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_relations=False):
        result = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'tenant_id': self.tenant_id,
            'is_authenticated': self.is_authenticated,
            'is_active': self.is_active,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_relations:
            result['tenant'] = self.tenant.to_dict() if self.tenant else None
            
        return result


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
