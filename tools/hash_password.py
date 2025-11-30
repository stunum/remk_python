#!/usr/bin/env python3
"""
密码哈希计算工具
用于计算数据库初始化时需要的密码哈希值
"""
import hashlib
import sys

# 密码盐值（优先从配置文件读取，确保与 utils/jwt_auth.py 中保持一致）
try:
    from config import config as app_config

    PASSWORD_SALT = app_config.config.jwt.password_salt
except Exception:
    # 配置加载失败时回退到默认盐值，并给出提示
    PASSWORD_SALT = "eyes_remk_system_salt_change_in_production"


def calculate_frontend_hash(password: str) -> str:
    """
    计算前端SHA-256哈希
    模拟前端加密过程
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def calculate_backend_hash(frontend_hash: str) -> str:
    """
    计算后端SHA-256+盐值哈希
    这是最终存储到数据库的值
    """
    salted = f"{frontend_hash}{PASSWORD_SALT}"
    return hashlib.sha256(salted.encode('utf-8')).hexdigest()


def hash_password(password: str) -> tuple:
    """
    计算完整的密码哈希
    返回 (前端哈希, 后端哈希)
    """
    frontend = calculate_frontend_hash(password)
    backend = calculate_backend_hash(frontend)
    return frontend, backend


def main():
    """主函数"""
    print("=" * 80)
    print("密码哈希计算工具")
    print("=" * 80)
    print()
    
    if len(sys.argv) > 1:
        # 从命令行参数读取密码
        password = sys.argv[1]
    else:
        # 交互式输入
        password = input("请输入要加密的密码: ")
    
    if not password:
        print("密码不能为空")
        sys.exit(1)
    
    # 计算哈希
    frontend_hash, backend_hash = hash_password(password)
    
    # 显示结果
    print()
    print("-" * 80)
    print("原始密码:")
    print(f"  {password}")
    print()
    print("前端SHA-256哈希 (API登录时使用):")
    print(f"  {frontend_hash}")
    print()
    print("后端SHA-256+盐值哈希 (数据库存储):")
    print(f"  {backend_hash}")
    print("-" * 80)
    print()
    
    # 生成SQL插入语句
    print("可用于 init_data.sql 的密码哈希值:")
    print(f"  password_hash = '{backend_hash}'")
    print()
    
    # 生成测试用的curl命令
    print("测试登录的curl命令:")
    print(f"""  curl -X POST "http://localhost:8000/api/auth/login" \\
    -H "Content-Type: application/json" \\
    -d '{{
      "username": "your_username",
      "password": "{frontend_hash}"
    }}'""")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()

