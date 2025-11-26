"""
订单状态管理工具函数
"""

from datetime import datetime
from models import Order, SupplyInfo


class OrderStatus:
    """订单状态常量"""
    PENDING = 'PENDING'                          # 待确认
    CONFIRMED = 'CONFIRMED'                      # 已确认
    SHIPPED = 'SHIPPED'                          # 已发货
    IN_TRANSIT = 'IN_TRANSIT'                    # 运输中
    DELIVERED = 'DELIVERED'                      # 已送达
    COMPLETED = 'COMPLETED'                      # 已完成
    CANCELLED_BY_PHARMACY = 'CANCELLED_BY_PHARMACY'      # 药店取消
    CANCELLED_BY_SUPPLIER = 'CANCELLED_BY_SUPPLIER'      # 供应商取消
    EXPIRED_CANCELLED = 'EXPIRED_CANCELLED'      # 超时取消


class OrderStatusTransition:
    """订单状态流转管理"""
    
    # 定义状态流转规则
    VALID_TRANSITIONS = {
        OrderStatus.PENDING: [
            OrderStatus.CONFIRMED,
            OrderStatus.CANCELLED_BY_PHARMACY,
            OrderStatus.CANCELLED_BY_SUPPLIER,
            OrderStatus.EXPIRED_CANCELLED
        ],
        OrderStatus.CONFIRMED: [
            OrderStatus.SHIPPED
        ],
        OrderStatus.SHIPPED: [
            OrderStatus.IN_TRANSIT
        ],
        OrderStatus.IN_TRANSIT: [
            OrderStatus.DELIVERED
        ],
        OrderStatus.DELIVERED: [
            OrderStatus.COMPLETED
        ]
        # 终态：COMPLETED, CANCELLED_BY_PHARMACY, CANCELLED_BY_SUPPLIER, EXPIRED_CANCELLED
    }
    
    # 状态中文描述
    STATUS_DESCRIPTIONS = {
        OrderStatus.PENDING: '待确认',
        OrderStatus.CONFIRMED: '已确认',
        OrderStatus.SHIPPED: '已发货',
        OrderStatus.IN_TRANSIT: '运输中',
        OrderStatus.DELIVERED: '已送达',
        OrderStatus.COMPLETED: '已完成',
        OrderStatus.CANCELLED_BY_PHARMACY: '药店取消',
        OrderStatus.CANCELLED_BY_SUPPLIER: '供应商取消',
        OrderStatus.EXPIRED_CANCELLED: '超时取消'
    }
    
    @classmethod
    def can_transition(cls, current_status, target_status):
        """检查是否可以从当前状态转换到目标状态"""
        if current_status not in cls.VALID_TRANSITIONS:
            return False
        
        return target_status in cls.VALID_TRANSITIONS[current_status]
    
    @classmethod
    def get_next_states(cls, current_status):
        """获取当前状态可以转换到的下一个状态列表"""
        return cls.VALID_TRANSITIONS.get(current_status, [])
    
    @classmethod
    def is_terminal_status(cls, status):
        """判断是否为终态"""
        return status not in cls.VALID_TRANSITIONS
    
    @classmethod
    def get_description(cls, status):
        """获取状态的中文描述"""
        return cls.STATUS_DESCRIPTIONS.get(status, status)


def validate_order_status_change(order, new_status):
    """
    验证订单状态变更是否合法
    
    Args:
        order: 订单对象
        new_status: 新状态
        
    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    if not order:
        return False, "订单不存在"
    
    current_status = order.status
    
    # 检查状态是否有变化
    if current_status == new_status:
        return False, "订单状态未发生变化"
    
    # 检查状态流转是否合法
    if not OrderStatusTransition.can_transition(current_status, new_status):
        current_desc = OrderStatusTransition.get_description(current_status)
        new_desc = OrderStatusTransition.get_description(new_status)
        return False, f"不能从 {current_desc} 状态转换到 {new_desc} 状态"
    
    return True, ""


def restore_supply_quantity(order):
    """
    恢复供应信息的可用数量
    当订单被取消时调用
    """
    try:
        for item in order.items:
            supply_info = SupplyInfo.query.filter_by(
                tenant_id=order.supplier_tenant_id,
                drug_id=item.drug_id,
                status='ACTIVE'
            ).first()
            
            if supply_info:
                supply_info.available_quantity += item.quantity
                supply_info.updated_at = datetime.utcnow()
    except Exception as e:
        raise Exception(f"恢复供应数量失败: {str(e)}")


def get_order_timeline(order):
    """
    获取订单时间线
    
    Args:
        order: 订单对象
        
    Returns:
        list: 时间线事件列表
    """
    timeline = []
    
    # 创建订单
    timeline.append({
        'status': OrderStatus.PENDING,
        'description': '订单已创建，等待供应商确认',
        'timestamp': order.created_at,
        'user': order.created_by_user.username if order.created_by_user else None
    })
    
    # 供应商确认
    if order.confirmed_at:
        timeline.append({
            'status': OrderStatus.CONFIRMED,
            'description': '供应商已确认订单',
            'timestamp': order.confirmed_at,
            'user': order.confirmed_by_user.username if order.confirmed_by_user else None
        })
    
    # 发货
    if order.shipped_at:
        timeline.append({
            'status': OrderStatus.SHIPPED,
            'description': f'已发货{f"，运单号：{order.tracking_number}" if order.tracking_number else ""}',
            'timestamp': order.shipped_at,
            'user': None  # 供应商发货，但没有记录具体用户
        })
    
    # 送达
    if order.delivered_at:
        timeline.append({
            'status': OrderStatus.DELIVERED,
            'description': '货物已送达目的地',
            'timestamp': order.delivered_at,
            'user': None  # 物流送达，但没有记录具体用户
        })
    
    # 收货确认
    if order.received_at:
        timeline.append({
            'status': OrderStatus.COMPLETED,
            'description': '药店已确认收货，订单完成',
            'timestamp': order.received_at,
            'user': order.received_confirmed_by_user.username if order.received_confirmed_by_user else None
        })
    
    # 取消
    if order.cancelled_at:
        cancel_desc = "订单已取消"
        if order.cancel_reason:
            cancel_desc += f"，原因：{order.cancel_reason}"
            
        timeline.append({
            'status': order.status,  # 保持实际的取消状态
            'description': cancel_desc,
            'timestamp': order.cancelled_at,
            'user': order.cancelled_by_user.username if order.cancelled_by_user else None
        })
    
    # 按时间排序
    timeline.sort(key=lambda x: x['timestamp'])
    
    return timeline
