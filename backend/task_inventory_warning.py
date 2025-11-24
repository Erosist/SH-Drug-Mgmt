"""
库存预警定时任务
实现每日凌晨执行库存预警扫描
"""
import schedule
import time
import logging
from datetime import datetime
from inventory_warning import scan_inventory_warnings

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('inventory_warning.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def daily_warning_scan():
    """
    每日预警扫描任务
    """
    try:
        logger.info("开始执行库存预警扫描")
        
        # 执行扫描
        result = scan_inventory_warnings()
        
        logger.info(f"预警扫描完成: {result}")
        
        # 如果有预警，记录详细信息
        if result['total_warnings'] > 0:
            logger.warning(f"发现 {result['total_warnings']} 个预警项，涉及 {result['affected_tenants']} 个企业")
        else:
            logger.info("未发现预警项")
            
    except Exception as e:
        logger.error(f"预警扫描失败: {str(e)}")


def start_scheduler():
    """
    启动定时任务调度器
    """
    # 每天凌晨2点执行预警扫描
    schedule.every().day.at("02:00").do(daily_warning_scan)
    
    logger.info("库存预警定时任务已启动，每日02:00执行扫描")
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
        except KeyboardInterrupt:
            logger.info("定时任务已停止")
            break
        except Exception as e:
            logger.error(f"定时任务执行出错: {str(e)}")
            time.sleep(60)


if __name__ == "__main__":
    # 立即执行一次扫描（用于测试）
    logger.info("执行初始扫描...")
    daily_warning_scan()
    
    # 启动定时任务
    start_scheduler()
