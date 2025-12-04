#!/usr/bin/env python3
"""
测试运行器 - 运行所有测试
"""
import sys
import os
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_frontend_tests():
    """运行前端测试"""
    print("🧪 运行前端测试...")
    frontend_dir = project_root / 'frontend'
    
    if not frontend_dir.exists():
        print("❌ 前端目录不存在")
        return False
    
    try:
        # 切换到前端目录
        os.chdir(frontend_dir)
        
        # 运行npm test
        result = subprocess.run(['npm', 'test'], 
                              capture_output=True, 
                              text=True, 
                              shell=True)
        
        if result.returncode == 0:
            print("✅ 前端测试通过")
            print(result.stdout)
            return True
        else:
            print("❌ 前端测试失败")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 前端测试执行错误: {e}")
        return False
    finally:
        # 切换回项目根目录
        os.chdir(project_root)

def run_backend_tests():
    """运行后端测试"""
    print("\n🧪 运行后端测试...")
    backend_dir = project_root / 'backend'
    
    if not backend_dir.exists():
        print("❌ 后端目录不存在")
        return False
    
    try:
        # 切换到后端目录
        os.chdir(backend_dir)
        
        # 设置测试环境变量
        os.environ['FLASK_ENV'] = 'testing'
        os.environ['TESTING'] = 'True'
        
        # 运行pytest
        result = subprocess.run(['python', '-m', 'pytest', '-v', 'tests/'], 
                              capture_output=True, 
                              text=True)
        
        if result.returncode == 0:
            print("✅ 后端测试通过")
            print(result.stdout)
            return True
        else:
            print("❌ 后端测试失败")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 后端测试执行错误: {e}")
        return False
    finally:
        # 切换回项目根目录
        os.chdir(project_root)

def run_specific_test(test_file):
    """运行特定测试文件"""
    if test_file.endswith('.js'):
        # 前端测试
        print(f"🧪 运行前端测试: {test_file}")
        frontend_dir = project_root / 'frontend'
        os.chdir(frontend_dir)
        result = subprocess.run(['npm', 'test', test_file], shell=True)
        return result.returncode == 0
    elif test_file.endswith('.py'):
        # 后端测试
        print(f"🧪 运行后端测试: {test_file}")
        backend_dir = project_root / 'backend'
        os.chdir(backend_dir)
        os.environ['FLASK_ENV'] = 'testing'
        result = subprocess.run(['python', '-m', 'pytest', '-v', test_file])
        return result.returncode == 0
    else:
        print(f"❌ 未知的测试文件类型: {test_file}")
        return False

def main():
    """主函数"""
    print("🚀 SH-Drug-Mgmt 测试套件")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        # 运行特定测试
        test_file = sys.argv[1]
        success = run_specific_test(test_file)
        sys.exit(0 if success else 1)
    
    # 运行所有测试
    frontend_success = run_frontend_tests()
    backend_success = run_backend_tests()
    
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    print(f"前端测试: {'✅ 通过' if frontend_success else '❌ 失败'}")
    print(f"后端测试: {'✅ 通过' if backend_success else '❌ 失败'}")
    
    if frontend_success and backend_success:
        print("🎉 所有测试通过!")
        sys.exit(0)
    else:
        print("💥 部分测试失败!")
        sys.exit(1)

if __name__ == '__main__':
    main()