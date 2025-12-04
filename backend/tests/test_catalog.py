"""
药品目录管理测试
"""
import pytest
import json
from datetime import datetime, timedelta
from models import User, Tenant, Drug, InventoryItem
from extensions import db


class TestCatalogAPI:
    """测试药品目录API"""
    
    @pytest.fixture
    def catalog_data(self, app):
        """创建目录测试数据"""
        with app.app_context():
            # 创建测试药品
            drugs = [
                Drug(
                    generic_name='阿莫西林',
                    brand_name='阿莫西林胶囊',
                    approval_number='H12345678901',
                    dosage_form='胶囊',
                    specification='250mg*24粒',
                    manufacturer='测试制药厂',
                    category='抗生素',
                    prescription_type='处方药'
                ),
                Drug(
                    generic_name='布洛芬',
                    brand_name='布洛芬片',
                    approval_number='H12345678902',
                    dosage_form='片剂',
                    specification='0.2g*20片',
                    manufacturer='测试制药厂2',
                    category='解热镇痛',
                    prescription_type='非处方药'
                )
            ]
            
            db.session.add_all(drugs)
            db.session.commit()
            
            # 创建测试企业
            tenants = [
                Tenant(
                    name='测试药店1',
                    type='PHARMACY',
                    unified_social_credit_code='91310000000000001X',
                    legal_representative='负责人1',
                    contact_person='联系人1',
                    contact_phone='13800138001',
                    contact_email='pharmacy1@test.com',
                    address='地址1',
                    business_scope='药品零售'
                ),
                Tenant(
                    name='测试供应商1',
                    type='SUPPLIER',
                    unified_social_credit_code='91310000000000002X',
                    legal_representative='负责人2',
                    contact_person='联系人2',
                    contact_phone='13800138002',
                    contact_email='supplier1@test.com',
                    address='地址2',
                    business_scope='药品批发'
                )
            ]
            
            db.session.add_all(tenants)
            db.session.commit()
            
            # 创建库存数据
            inventory_items = [
                InventoryItem(
                    drug_id=drugs[0].id,
                    tenant_id=tenants[0].id,
                    batch_number='BATCH001',
                    production_date=datetime.now().date() - timedelta(days=30),
                    expiry_date=datetime.now().date() + timedelta(days=365),
                    quantity=100,
                    unit_price=25.50
                ),
                InventoryItem(
                    drug_id=drugs[1].id,
                    tenant_id=tenants[0].id,
                    batch_number='BATCH002',
                    production_date=datetime.now().date() - timedelta(days=60),
                    expiry_date=datetime.now().date() + timedelta(days=300),
                    quantity=50,
                    unit_price=15.80
                )
            ]
            
            db.session.add_all(inventory_items)
            db.session.commit()
            
            return {
                'drugs': drugs,
                'tenants': tenants,
                'inventory_items': inventory_items
            }
    
    def test_drugs_list_endpoint(self, client, catalog_data):
        """测试药品列表接口"""
        response = client.get('/api/catalog/drugs')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 2
        
        # 验证药品数据结构
        drug = data[0]
        required_fields = ['id', 'generic_name', 'brand_name', 'approval_number', 
                          'dosage_form', 'specification', 'manufacturer']
        for field in required_fields:
            assert field in drug
    
    def test_drugs_search_by_name(self, client, catalog_data):
        """测试药品名称搜索"""
        response = client.get('/api/catalog/drugs?search=阿莫西林')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) >= 1
        assert '阿莫西林' in data[0]['generic_name']
    
    def test_drugs_filter_by_category(self, client, catalog_data):
        """测试按类别筛选药品"""
        response = client.get('/api/catalog/drugs?category=抗生素')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) >= 1
        assert data[0]['category'] == '抗生素'
    
    def test_tenants_list_endpoint(self, client, catalog_data):
        """测试企业列表接口"""
        response = client.get('/api/catalog/tenants')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 2
        
        # 验证企业数据结构
        tenant = data[0]
        required_fields = ['id', 'name', 'type', 'unified_social_credit_code', 
                          'contact_person', 'contact_phone']
        for field in required_fields:
            assert field in tenant
    
    def test_tenants_filter_by_type(self, client, catalog_data):
        """测试按类型筛选企业"""
        response = client.get('/api/catalog/tenants?type=PHARMACY')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) >= 1
        for tenant in data:
            assert tenant['type'] == 'PHARMACY'
    
    def test_tenant_detail_endpoint(self, client, catalog_data):
        """测试企业详情接口"""
        tenant_id = catalog_data['tenants'][0].id
        response = client.get(f'/api/catalog/tenants/{tenant_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == tenant_id
        assert data['name'] == '测试药店1'
    
    def test_inventory_list_endpoint(self, client, catalog_data):
        """测试库存列表接口"""
        response = client.get('/api/catalog/inventory')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 2
        
        # 验证库存数据结构
        item = data[0]
        required_fields = ['id', 'drug_id', 'tenant_id', 'batch_number', 
                          'quantity', 'unit_price', 'expiry_date']
        for field in required_fields:
            assert field in item
    
    def test_inventory_filter_by_tenant(self, client, catalog_data):
        """测试按企业筛选库存"""
        tenant_id = catalog_data['tenants'][0].id
        response = client.get(f'/api/catalog/inventory?tenant_id={tenant_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) >= 1
        for item in data:
            assert item['tenant_id'] == tenant_id
    
    def test_inventory_filter_by_drug(self, client, catalog_data):
        """测试按药品筛选库存"""
        drug_id = catalog_data['drugs'][0].id
        response = client.get(f'/api/catalog/inventory?drug_id={drug_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) >= 1
        for item in data:
            assert item['drug_id'] == drug_id


class TestCatalogValidation:
    """测试目录API验证"""
    
    def test_invalid_tenant_id(self, client):
        """测试无效企业ID"""
        response = client.get('/api/catalog/tenants/99999')
        assert response.status_code == 404
    
    def test_invalid_query_parameters(self, client):
        """测试无效查询参数"""
        # 测试无效的企业类型
        response = client.get('/api/catalog/tenants?type=INVALID')
        assert response.status_code == 200  # 应该返回空列表
        data = response.get_json()
        assert len(data) == 0
        
        # 测试无效的分页参数
        response = client.get('/api/catalog/drugs?page=-1')
        assert response.status_code in [200, 400]  # 根据实现决定