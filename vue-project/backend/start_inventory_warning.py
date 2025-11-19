#!/usr/bin/env python3
"""
库存预警功能快速启动脚本
"""
import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """检查依赖包"""
    try:
        import flask
        import flask_sqlalchemy  
        import flask_migrate
        import flask_jwt_extended
        import schedule
        print("✅ 所有依赖包已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def init_database():
    """初始化数据库"""
    try:
        print("📊 初始化数据库...")
        # 初始化数据库需要在应用上下文中运行
        from app import create_app
        from models import db
        
        app = create_app()
        with app.app_context():
            db.create_all()
        print("✅ 数据库初始化完成")
        return True
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False

def create_test_data():
    """创建测试数据"""
    try:
        print("🧪 创建测试数据...")
        # 导入并运行测试数据创建脚本，需要在应用上下文中运行
        from app import create_app
        from create_warning_test_data import create_test_data as create_data_func
        
        app = create_app()
        with app.app_context():
            create_data_func()
        print("✅ 测试数据创建完成")
        return True
    except Exception as e:
        print(f"❌ 创建测试数据失败: {e}")
        return False

def start_server():
    """启动Flask服务器"""
    try:
        print("🚀 启动Flask服务器...")
        print("服务器将在 http://localhost:5000 启动")
        print("按 Ctrl+C 停止服务器")
        print("-" * 50)
        
        # 启动Flask应用
        from run import app
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动服务器失败: {e}")

def start_scheduler():
    """启动定时任务调度器"""
    try:
        print("⏰ 启动定时任务调度器...")
        print("预警扫描将在每日02:00执行")
        print("按 Ctrl+C 停止调度器")
        print("-" * 50)
        
        from task_inventory_warning import start_scheduler
        start_scheduler()
        
    except KeyboardInterrupt:
        print("\n👋 定时任务调度器已停止")
    except Exception as e:
        print(f"❌ 启动定时任务失败: {e}")

def run_tests():
    """运行测试"""
    try:
        print("🧪 运行预警功能测试...")
        
        # 检查是否安装了requests
        try:
            import requests
        except ImportError:
            print("安装测试依赖...")
            subprocess.run([sys.executable, "-m", "pip", "install", "requests"])
        
        from test_inventory_warning import main
        main()
        
    except Exception as e:
        print(f"❌ 运行测试失败: {e}")

def show_help():
    """显示帮助信息"""
    help_text = """
📋 库存预警功能启动脚本

用法: python start_inventory_warning.py [命令]

可用命令:
  server    启动Flask服务器 (默认)
  scheduler 启动定时任务调度器
  test      运行功能测试
  init      初始化数据库和测试数据
  help      显示此帮助信息

示例:
  python start_inventory_warning.py          # 启动服务器
  python start_inventory_warning.py server   # 启动服务器
  python start_inventory_warning.py scheduler # 启动定时任务
  python start_inventory_warning.py test     # 运行测试
  python start_inventory_warning.py init     # 初始化数据

注意:
- 首次运行请先执行 init 命令
- 服务器和定时任务需要分别在不同终端运行
- 确保已安装所有依赖: pip install -r requirements.txt
"""
    print(help_text)

def main():
    """主函数"""
    # 解析命令行参数
    command = sys.argv[1] if len(sys.argv) > 1 else "server"
    
    print("🔄 库存预警功能启动器")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 执行对应命令
    if command == "server":
        start_server()
    elif command == "scheduler":
        start_scheduler()
    elif command == "test":
        run_tests()
    elif command == "init":
        if init_database():
            create_test_data()
    elif command == "help":
        show_help()
    else:
        print(f"❌ 未知命令: {command}")
        show_help()

if __name__ == "__main__":
    main()
