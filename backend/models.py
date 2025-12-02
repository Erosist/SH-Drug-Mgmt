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


class Tenant(db.Model):
    """企业租户模型 - 统一的租户表"""
    __tablename__ = 'tenants'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    type = db.Column(db.String(40), nullable=False)  # PHARMACY, SUPPLIER, LOGISTICS, REGULATOR
    unified_social_credit_code = db.Column(db.String(40), unique=True, nullable=False)
    legal_representative = db.Column(db.String(60), nullable=False)
    contact_person = db.Column(db.String(60), nullable=False)
    contact_phone = db.Column(db.String(40), nullable=False)
    contact_email = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    business_scope = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    # 地理位置信息（用于就近推荐）
    latitude = db.Column(db.Float, nullable=True)  # 纬度
    longitude = db.Column(db.Float, nullable=True)  # 经度
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    supply_infos = db.relationship('SupplyInfo', backref='tenant', lazy=True)
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
            'latitude': self.latitude,
            'longitude': self.longitude,
            'created_at': to_iso(self.created_at),
            'updated_at': to_iso(self.updated_at)
        }


class Drug(db.Model):
    """药品主数据模型 - 统一的药品表"""
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    supply_infos = db.relationship('SupplyInfo', backref='drug', lazy=True)
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
            'updated_at': to_iso(self.updated_at)
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
            'created_at': to_iso(self.created_at),
            'updated_at': to_iso(self.updated_at)
        }
        
        if include_relations:
            result.update({
                'tenant': self.tenant.to_dict() if self.tenant else None,
                'drug': self.drug.to_dict() if self.drug else None
            })
        
        return result


class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(30), unique=True, nullable=True)
    real_name = db.Column(db.String(120), nullable=True)
    company_name = db.Column(db.String(160), nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='unauth')
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True, index=True)
    is_authenticated = db.Column(db.Boolean, nullable=False, default=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    last_login_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
            'real_name': self.real_name,
            'company_name': self.company_name,
            'role': self.role,
            'tenant_id': self.tenant_id,
            'is_authenticated': self.is_authenticated,
            'is_active': self.is_active,
            'last_login_at': to_iso(self.last_login_at),
            'created_at': to_iso(self.created_at),
            'updated_at': to_iso(self.updated_at),
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


class EnterpriseCertification(db.Model):
    __tablename__ = 'enterprise_certifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    role = db.Column(db.String(20), nullable=False)
    company_name = db.Column(db.String(160), nullable=False)
    unified_social_credit_code = db.Column(db.String(60), nullable=False)
    contact_person = db.Column(db.String(80), nullable=False)
    contact_phone = db.Column(db.String(40), nullable=False)
    contact_email = db.Column(db.String(160), nullable=False)
    registered_address = db.Column(db.String(255), nullable=False)
    business_scope = db.Column(db.Text, nullable=False)
    qualification_files = db.Column(db.JSON, nullable=True)
    status = db.Column(db.String(20), default='pending', nullable=False)
    reject_reason = db.Column(db.Text, nullable=True)
    attempt_count = db.Column(db.Integer, default=1, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('enterprise_certification', uselist=False))
    reviewer = db.relationship('User', foreign_keys=[reviewer_id])

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'reviewer_id': self.reviewer_id,
            'role': self.role,
            'company_name': self.company_name,
            'unified_social_credit_code': self.unified_social_credit_code,
            'contact_person': self.contact_person,
            'contact_phone': self.contact_phone,
            'contact_email': self.contact_email,
            'registered_address': self.registered_address,
            'business_scope': self.business_scope,
            'qualification_files': self.qualification_files or [],
            'status': self.status,
            'reject_reason': self.reject_reason,
            'attempt_count': self.attempt_count,
            'submitted_at': to_iso(self.submitted_at),
            'reviewed_at': to_iso(self.reviewed_at),
            'created_at': to_iso(self.created_at),
            'updated_at': to_iso(self.updated_at),
        }


class EnterpriseReviewLog(db.Model):
    __tablename__ = 'enterprise_review_logs'

    id = db.Column(db.Integer, primary_key=True)
    certification_id = db.Column(db.Integer, db.ForeignKey('enterprise_certifications.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    decision = db.Column(db.String(20), nullable=False)
    reason_code = db.Column(db.String(64), nullable=True)
    reason_text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    certification = db.relationship('EnterpriseCertification', backref=db.backref('review_logs', lazy=True))
    reviewer = db.relationship('User', foreign_keys=[reviewer_id])

    def to_dict(self):
        return {
            'id': self.id,
            'certification_id': self.certification_id,
            'reviewer_id': self.reviewer_id,
            'decision': self.decision,
            'reason_code': self.reason_code,
            'reason_text': self.reason_text,
            'created_at': to_iso(self.created_at),
        }


class InventoryItem(db.Model):
    __tablename__ = 'inventory_items'

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    drug_id = db.Column(db.Integer, db.ForeignKey('drugs.id'), nullable=False)
    batch_number = db.Column(db.String(60), nullable=False)
    production_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def is_low_stock(self):
        """判断是否低库存（库存数量低于10件）"""
        return self.quantity < 10
    
    @property
    def is_near_expiry(self):
        """判断是否近效期（30天内到期）"""
        from datetime import timedelta
        threshold = datetime.utcnow().date() + timedelta(days=30)
        return self.expiry_date <= threshold
    
    @property
    def is_expired(self):
        """判断是否已过期"""
        return self.expiry_date <= datetime.utcnow().date()
    
    @property
    def days_to_expiry(self):
        """距离过期还有多少天"""
        delta = self.expiry_date - datetime.utcnow().date()
        return delta.days

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
            'is_low_stock': self.is_low_stock,
            'is_near_expiry': self.is_near_expiry,
            'is_expired': self.is_expired,
            'days_to_expiry': self.days_to_expiry
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


class Order(db.Model):
    """订单模型"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)  # 业务订单号
    buyer_tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    supplier_tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    supply_info_id = db.Column(db.Integer, db.ForeignKey('supply_info.id'), nullable=True, index=True)
    expected_delivery_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text)
    status = db.Column(db.String(30), nullable=False, default='PENDING')  # 订单状态
    logistics_tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True)
    tracking_number = db.Column(db.String(100), nullable=True)
    shipped_at = db.Column(db.DateTime, nullable=True)
    delivered_at = db.Column(db.DateTime, nullable=True)
    received_at = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    confirmed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    confirmed_at = db.Column(db.DateTime, nullable=True)
    received_confirmed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    cancelled_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    cancel_reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    buyer_tenant = db.relationship('Tenant', foreign_keys=[buyer_tenant_id], backref='buyer_orders')
    supplier_tenant = db.relationship('Tenant', foreign_keys=[supplier_tenant_id], backref='supplier_orders')
    supply_info = db.relationship('SupplyInfo', foreign_keys=[supply_info_id])
    logistics_tenant = db.relationship('Tenant', foreign_keys=[logistics_tenant_id])
    created_by_user = db.relationship('User', foreign_keys=[created_by], backref='created_orders')
    confirmed_by_user = db.relationship('User', foreign_keys=[confirmed_by])
    received_confirmed_by_user = db.relationship('User', foreign_keys=[received_confirmed_by])
    cancelled_by_user = db.relationship('User', foreign_keys=[cancelled_by])
    
    # 订单明细项
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super(Order, self).__init__(**kwargs)
        if not self.order_number:
            self.order_number = self.generate_order_number()

    def generate_order_number(self):
        """生成订单号：PH/SP + YYYYMMDD + 3位序号"""
        from datetime import date
        import random
        
        # 根据买方类型生成前缀
        prefix = 'PH'  # 默认药店
        if hasattr(self, 'buyer_tenant') and self.buyer_tenant:
            if self.buyer_tenant.type == 'SUPPLIER':
                prefix = 'SP'
            elif self.buyer_tenant.type == 'LOGISTICS':
                prefix = 'LG'
        
        today = date.today().strftime('%Y%m%d')
        # 生成3位随机数序号（实际项目中应该从数据库序列获取）
        sequence = str(random.randint(1, 999)).zfill(3)
        
        return f"{prefix}{today}{sequence}"

    @property
    def total_amount(self):
        """计算订单总金额"""
        return sum(item.total_amount for item in self.items)
    
    @property
    def total_quantity(self):
        """计算订单总数量"""
        return sum(item.quantity for item in self.items)

    def to_dict(self, include_relations=False):
        result = {
            'id': self.id,
            'order_number': self.order_number,
            'buyer_tenant_id': self.buyer_tenant_id,
            'supplier_tenant_id': self.supplier_tenant_id,
            'expected_delivery_date': self.expected_delivery_date.isoformat() if self.expected_delivery_date else None,
            'notes': self.notes,
            'status': self.status,
            'logistics_tenant_id': self.logistics_tenant_id,
            'tracking_number': self.tracking_number,
            'shipped_at': to_iso(self.shipped_at),
            'delivered_at': to_iso(self.delivered_at),
            'received_at': to_iso(self.received_at),
            'created_by': self.created_by,
            'confirmed_by': self.confirmed_by,
            'confirmed_at': to_iso(self.confirmed_at),
            'received_confirmed_by': self.received_confirmed_by,
            'cancelled_by': self.cancelled_by,
            'cancelled_at': to_iso(self.cancelled_at),
            'cancel_reason': self.cancel_reason,
            'created_at': to_iso(self.created_at),
            'updated_at': to_iso(self.updated_at),
            'total_amount': self.total_amount,
            'total_quantity': self.total_quantity
        }
        
        if include_relations:
            result.update({
                'buyer_tenant': self.buyer_tenant.to_dict() if self.buyer_tenant else None,
                'supplier_tenant': self.supplier_tenant.to_dict() if self.supplier_tenant else None,
                'logistics_tenant': self.logistics_tenant.to_dict() if self.logistics_tenant else None,
                'created_by_user': self.created_by_user.to_dict() if self.created_by_user else None,
                'confirmed_by_user': self.confirmed_by_user.to_dict() if self.confirmed_by_user else None,
                'items': [item.to_dict(include_relations=True) for item in self.items]
            })
        
        return result


class OrderItem(db.Model):
    """订单明细模型"""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, index=True)
    drug_id = db.Column(db.Integer, db.ForeignKey('drugs.id'), nullable=False)
    batch_number = db.Column(db.String(50), nullable=True)  # 指定批号（可选）
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)  # 成交单价
    quantity = db.Column(db.Integer, nullable=False)  # 订购数量
    
    # 关联关系
    drug = db.relationship('Drug', backref='order_items')

    @property
    def total_amount(self):
        """计算明细金额"""
        return float(self.unit_price) * self.quantity if self.unit_price else 0.0

    def to_dict(self, include_relations=False):
        result = {
            'id': self.id,
            'order_id': self.order_id,
            'drug_id': self.drug_id,
            'batch_number': self.batch_number,
            'unit_price': float(self.unit_price) if self.unit_price else None,
            'quantity': self.quantity,
            'total_amount': self.total_amount
        }
        
        if include_relations:
            result.update({
                'drug': self.drug.to_dict() if self.drug else None
            })
        
        return result


class InventoryTransaction(db.Model):
    """库存流水模型"""
    __tablename__ = 'inventory_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False, index=True)
    transaction_type = db.Column(db.String(20), nullable=False)  # IN, OUT, ADJUST, TRANSFER
    quantity_delta = db.Column(db.Integer, nullable=False)  # 数量变动
    source_tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True)  # 对端企业
    related_order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=True)  # 关联订单
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联关系
    inventory_item = db.relationship('InventoryItem', backref='transactions')
    source_tenant = db.relationship('Tenant')
    related_order = db.relationship('Order')
    created_by_user = db.relationship('User')
    
    def to_dict(self, include_relations=False):
        result = {
            'id': self.id,
            'inventory_item_id': self.inventory_item_id,
            'transaction_type': self.transaction_type,
            'quantity_delta': self.quantity_delta,
            'source_tenant_id': self.source_tenant_id,
            'related_order_id': self.related_order_id,
            'notes': self.notes,
            'created_by': self.created_by,
            'created_at': to_iso(self.created_at)
        }
        
        if include_relations:
            result.update({
                'inventory_item': self.inventory_item.to_dict() if self.inventory_item else None,
                'source_tenant': self.source_tenant.to_dict() if self.source_tenant else None,
                'related_order': self.related_order.to_dict() if self.related_order else None,
                'created_by_user': self.created_by_user.to_dict() if self.created_by_user else None
            })
        
        return result


class CirculationRecord(db.Model):
    """流通记录模型 - 用于记录药品在运输过程中的状态变化"""
    __tablename__ = 'circulation_records'
    
    id = db.Column(db.Integer, primary_key=True)
    tracking_number = db.Column(db.String(100), nullable=False, index=True)  # 运单号（订单运单号）
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=True, index=True)
    batch_number = db.Column(db.String(60), nullable=True, index=True)  # 药品批号（用于追溯，冗余字段）
    transport_status = db.Column(db.String(20), nullable=False)  # SHIPPED, IN_TRANSIT, DELIVERED
    reported_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 上报用户
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    current_location = db.Column(db.String(500), nullable=True)  # GPS坐标或文字地址
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    remarks = db.Column(db.Text, nullable=True)  # 备注信息
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # 关联关系
    order = db.relationship('Order', backref='circulation_records')
    reporter = db.relationship('User', backref='reported_circulation_records')
    
    def to_dict(self, include_relations=False):
        result = {
            'id': self.id,
            'tracking_number': self.tracking_number,
            'order_id': self.order_id,
            'batch_number': self.batch_number,
            'transport_status': self.transport_status,
            'reported_by': self.reported_by,
            'timestamp': to_iso(self.timestamp) if self.timestamp else None,
            'current_location': self.current_location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'remarks': self.remarks,
            'created_at': to_iso(self.created_at) if self.created_at else None
        }
        
        if include_relations:
            if self.order:
                result['order'] = self.order.to_dict()
            if self.reporter:
                result['reporter'] = self.reporter.to_dict()
        
        return result