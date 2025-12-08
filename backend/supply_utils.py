"""
供应信息管理工具模块
"""

from datetime import datetime
from flask import current_app
from extensions import db
from models import SupplyInfo


def update_supply_info_quantity(tenant_id, drug_id, quantity_delta, operation_desc="", supply_info_id=None):
    """
    更新供应信息的可用数量，并自动管理上下架状态
    
    Args:
        tenant_id: 供应商企业ID
        drug_id: 药品ID  
        quantity_delta: 数量变化（正数表示增加，负数表示减少）
        operation_desc: 操作描述（用于日志）
        supply_info_id: 可选，直接指定要更新的供应信息ID
    
    Returns:
        SupplyInfo: 更新后的供应信息对象，如果没找到则返回None
    """
    # 如果提供了supply_info_id，直接使用它
    if supply_info_id:
        supply_info = SupplyInfo.query.get(supply_info_id)
        if not supply_info:
            if current_app:
                current_app.logger.warning(f'未找到供应信息ID {supply_info_id}')
            else:
                print(f'WARNING: 未找到供应信息ID {supply_info_id}')
            return None
        
        # 验证租户和药品ID是否匹配（安全检查）
        if supply_info.tenant_id != tenant_id or supply_info.drug_id != drug_id:
            if current_app:
                current_app.logger.error(f'供应信息ID {supply_info_id} 的租户或药品ID不匹配')
            else:
                print(f'ERROR: 供应信息ID {supply_info_id} 的租户或药品ID不匹配')
            return None
    else:
        # 先尝试查找ACTIVE状态的供应信息
        supply_info = SupplyInfo.query.filter_by(
            tenant_id=tenant_id,
            drug_id=drug_id,
            status='ACTIVE'
        ).first()
        
        # 如果没找到ACTIVE状态的，再查找INACTIVE状态的
        if not supply_info:
            supply_info = SupplyInfo.query.filter_by(
                tenant_id=tenant_id,
                drug_id=drug_id,
                status='INACTIVE'
            ).first()
    
    if not supply_info:
        if current_app:
            current_app.logger.warning(f'未找到供应商{tenant_id}的药品{drug_id}的供应信息')
        else:
            print(f'WARNING: 未找到供应商{tenant_id}的药品{drug_id}的供应信息')
        return None
    
    old_quantity = supply_info.available_quantity
    new_quantity = old_quantity + quantity_delta
    
    # 防止数量变为负数
    if new_quantity < 0:
        if current_app:
            current_app.logger.error(f'供应信息{supply_info.id}的可用数量不足，当前{old_quantity}，尝试变更{quantity_delta}')
        else:
            print(f'ERROR: 供应信息{supply_info.id}的可用数量不足，当前{old_quantity}，尝试变更{quantity_delta}')
        return None
    
    supply_info.available_quantity = new_quantity
    supply_info.updated_at = datetime.utcnow()
    
    # 状态管理逻辑
    if old_quantity == 0 and new_quantity > 0:
        # 从0恢复到大于0，自动上架
        supply_info.status = 'ACTIVE'
        log_msg = f'供应信息{supply_info.id}可供数量从0恢复到{new_quantity}，自动上架。{operation_desc}'
        if current_app:
            current_app.logger.info(log_msg)
        else:
            print(f'INFO: {log_msg}')
    elif old_quantity > 0 and new_quantity == 0:
        # 从大于0变为0，自动下架
        supply_info.status = 'INACTIVE'
        log_msg = f'供应信息{supply_info.id}可供数量从{old_quantity}变为0，自动下架。{operation_desc}'
        if current_app:
            current_app.logger.info(log_msg)
        else:
            print(f'INFO: {log_msg}')
    elif new_quantity > 0 and supply_info.status == 'INACTIVE':
        # 如果数量大于0但状态是INACTIVE（可能是手动下架），保持INACTIVE状态
        log_msg = f'供应信息{supply_info.id}数量{old_quantity}->{new_quantity}，但保持INACTIVE状态。{operation_desc}'
        if current_app:
            current_app.logger.info(log_msg)
        else:
            print(f'INFO: {log_msg}')
    else:
        log_msg = f'供应信息{supply_info.id}数量{old_quantity}->{new_quantity}。{operation_desc}'
        if current_app:
            current_app.logger.info(log_msg)
        else:
            print(f'INFO: {log_msg}')
    
    # 不在这里提交，让调用方管理事务
    return supply_info
