#!/usr/bin/env python3
"""
数据库初始化脚本

步骤：
1. 使用提供的账号连接默认 postgres 数据库，检查并创建 eyes_db 数据库；
2. 根据 SQLModel 模型创建缺失的数据表；
3. 初始化 users、examination_types、roles、permissions、user_roles、role_permissions 表的基础数据。
"""

from datetime import datetime
from typing import Dict, Iterable, List
import hashlib

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import ProgrammingError
from sqlmodel import Session, SQLModel, select

from models import (
    ExaminationType,
    Permission,
    Role,
    RolePermission,
    User,
    UserRole,
)
from utils.jwt_auth import PASSWORD_SALT, hash_password as backend_hash_password


POSTGRES_CONFIG: Dict[str, str] = {
    "host": "127.0.0.1",
    "port": "5432",
    "user": "postgres",
    "password": "1234",
}
TARGET_DB = "eyes_db"
DEFAULT_DB = "postgres"


# === 数据定义 ===
DEFAULT_ADMIN_PASSWORD = "admin123"
DEFAULT_ADMIN_PROFILE = {
    "username": "admin",
    "email": "admin@eyesremk.com",
    "phone": "13800000000",
    "full_name": "系统管理员",
    "user_type": "admin",
    "department": "管理部",
    "title": "系统管理员",
    "status": "active",
}

DEFAULT_ROLES: List[Dict[str, object]] = [
    {
        "role_name": "系统管理员",
        "role_code": "ROLE_ADMIN",
        "description": "系统最高权限管理员，拥有所有权限",
        "is_system_role": True,
        "is_active": True,
    },
    {
        "role_name": "医生",
        "role_code": "ROLE_DOCTOR",
        "description": "医生角色，可进行诊断、检查、患者管理等操作",
        "is_system_role": True,
        "is_active": True,
    },
    {
        "role_name": "技师",
        "role_code": "ROLE_TECHNICIAN",
        "description": "技师角色，可操作设备、采集图像、查看患者信息",
        "is_system_role": True,
        "is_active": True,
    },
    {
        "role_name": "查看者",
        "role_code": "ROLE_VIEWER",
        "description": "只读权限，可查看数据但不能修改",
        "is_system_role": True,
        "is_active": True,
    },
]

DEFAULT_PERMISSIONS: List[Dict[str, object]] = [
    # 用户管理
    {
        "permission_name": "查看用户",
        "permission_code": "USER_VIEW",
        "resource": "user",
        "action": "view",
        "description": "查看用户信息",
        "is_active": True,
    },
    {
        "permission_name": "创建用户",
        "permission_code": "USER_CREATE",
        "resource": "user",
        "action": "create",
        "description": "创建新用户",
        "is_active": True,
    },
    {
        "permission_name": "编辑用户",
        "permission_code": "USER_EDIT",
        "resource": "user",
        "action": "edit",
        "description": "编辑用户信息",
        "is_active": True,
    },
    {
        "permission_name": "删除用户",
        "permission_code": "USER_DELETE",
        "resource": "user",
        "action": "delete",
        "description": "删除用户",
        "is_active": True,
    },
    # 患者管理
    {
        "permission_name": "查看患者",
        "permission_code": "PATIENT_VIEW",
        "resource": "patient",
        "action": "view",
        "description": "查看患者信息",
        "is_active": True,
    },
    {
        "permission_name": "创建患者",
        "permission_code": "PATIENT_CREATE",
        "resource": "patient",
        "action": "create",
        "description": "创建患者档案",
        "is_active": True,
    },
    {
        "permission_name": "编辑患者",
        "permission_code": "PATIENT_EDIT",
        "resource": "patient",
        "action": "edit",
        "description": "编辑患者信息",
        "is_active": True,
    },
    {
        "permission_name": "删除患者",
        "permission_code": "PATIENT_DELETE",
        "resource": "patient",
        "action": "delete",
        "description": "删除患者档案",
        "is_active": True,
    },
    # 检查管理
    {
        "permission_name": "查看检查",
        "permission_code": "EXAMINATION_VIEW",
        "resource": "examination",
        "action": "view",
        "description": "查看检查记录",
        "is_active": True,
    },
    {
        "permission_name": "创建检查",
        "permission_code": "EXAMINATION_CREATE",
        "resource": "examination",
        "action": "create",
        "description": "创建检查记录",
        "is_active": True,
    },
    {
        "permission_name": "编辑检查",
        "permission_code": "EXAMINATION_EDIT",
        "resource": "examination",
        "action": "edit",
        "description": "编辑检查记录",
        "is_active": True,
    },
    {
        "permission_name": "删除检查",
        "permission_code": "EXAMINATION_DELETE",
        "resource": "examination",
        "action": "delete",
        "description": "删除检查记录",
        "is_active": True,
    },
    # 图像管理
    {
        "permission_name": "查看图像",
        "permission_code": "IMAGE_VIEW",
        "resource": "image",
        "action": "view",
        "description": "查看眼底图像",
        "is_active": True,
    },
    {
        "permission_name": "上传图像",
        "permission_code": "IMAGE_UPLOAD",
        "resource": "image",
        "action": "upload",
        "description": "上传眼底图像",
        "is_active": True,
    },
    {
        "permission_name": "删除图像",
        "permission_code": "IMAGE_DELETE",
        "resource": "image",
        "action": "delete",
        "description": "删除眼底图像",
        "is_active": True,
    },
    # 挂号管理
    {
        "permission_name": "查看挂号",
        "permission_code": "REGISTRATION_VIEW",
        "resource": "registration",
        "action": "view",
        "description": "查看挂号信息",
        "is_active": True,
    },
    {
        "permission_name": "创建挂号",
        "permission_code": "REGISTRATION_CREATE",
        "resource": "registration",
        "action": "create",
        "description": "创建挂号记录",
        "is_active": True,
    },
    {
        "permission_name": "编辑挂号",
        "permission_code": "REGISTRATION_EDIT",
        "resource": "registration",
        "action": "edit",
        "description": "编辑挂号信息",
        "is_active": True,
    },
    {
        "permission_name": "删除挂号",
        "permission_code": "REGISTRATION_DELETE",
        "resource": "registration",
        "action": "delete",
        "description": "删除挂号记录",
        "is_active": True,
    },
    # 诊断管理
    {
        "permission_name": "查看诊断",
        "permission_code": "DIAGNOSIS_VIEW",
        "resource": "diagnosis",
        "action": "view",
        "description": "查看诊断记录",
        "is_active": True,
    },
    {
        "permission_name": "创建诊断",
        "permission_code": "DIAGNOSIS_CREATE",
        "resource": "diagnosis",
        "action": "create",
        "description": "创建诊断记录",
        "is_active": True,
    },
    {
        "permission_name": "编辑诊断",
        "permission_code": "DIAGNOSIS_EDIT",
        "resource": "diagnosis",
        "action": "edit",
        "description": "编辑诊断记录",
        "is_active": True,
    },
    {
        "permission_name": "删除诊断",
        "permission_code": "DIAGNOSIS_DELETE",
        "resource": "diagnosis",
        "action": "delete",
        "description": "删除诊断记录",
        "is_active": True,
    },
    # 随访管理
    {
        "permission_name": "查看随访",
        "permission_code": "FOLLOWUP_VIEW",
        "resource": "followup",
        "action": "view",
        "description": "查看随访计划",
        "is_active": True,
    },
    {
        "permission_name": "创建随访",
        "permission_code": "FOLLOWUP_CREATE",
        "resource": "followup",
        "action": "create",
        "description": "创建随访计划",
        "is_active": True,
    },
    {
        "permission_name": "编辑随访",
        "permission_code": "FOLLOWUP_EDIT",
        "resource": "followup",
        "action": "edit",
        "description": "编辑随访计划",
        "is_active": True,
    },
    {
        "permission_name": "删除随访",
        "permission_code": "FOLLOWUP_DELETE",
        "resource": "followup",
        "action": "delete",
        "description": "删除随访计划",
        "is_active": True,
    },
    # 系统管理
    {
        "permission_name": "系统设置",
        "permission_code": "SYSTEM_SETTINGS",
        "resource": "system",
        "action": "settings",
        "description": "系统设置管理",
        "is_active": True,
    },
    {
        "permission_name": "查看日志",
        "permission_code": "SYSTEM_LOGS",
        "resource": "system",
        "action": "logs",
        "description": "查看系统日志",
        "is_active": True,
    },
    {
        "permission_name": "角色管理",
        "permission_code": "ROLE_MANAGE",
        "resource": "role",
        "action": "manage",
        "description": "管理角色",
        "is_active": True,
    },
    {
        "permission_name": "权限管理",
        "permission_code": "PERMISSION_MANAGE",
        "resource": "permission",
        "action": "manage",
        "description": "管理权限",
        "is_active": True,
    },
    # 检查类型管理
    {
        "permission_name": "查看检查类型",
        "permission_code": "EXAMINATION_TYPE_VIEW",
        "resource": "examination_type",
        "action": "view",
        "description": "查看检查类型信息",
        "is_active": True,
    },
    {
        "permission_name": "创建检查类型",
        "permission_code": "EXAMINATION_TYPE_CREATE",
        "resource": "examination_type",
        "action": "create",
        "description": "创建新的检查类型",
        "is_active": True,
    },
    {
        "permission_name": "编辑检查类型",
        "permission_code": "EXAMINATION_TYPE_EDIT",
        "resource": "examination_type",
        "action": "edit",
        "description": "编辑检查类型信息",
        "is_active": True,
    },
    {
        "permission_name": "删除检查类型",
        "permission_code": "EXAMINATION_TYPE_DELETE",
        "resource": "examination_type",
        "action": "delete",
        "description": "删除检查类型",
        "is_active": True,
    },
    # 角色权限分配
    {
        "permission_name": "分配角色权限",
        "permission_code": "ROLE_PERMISSION_ASSIGN",
        "resource": "role_permission",
        "action": "assign",
        "description": "为角色分配权限",
        "is_active": True,
    },
    # 用户角色分配
    {
        "permission_name": "分配用户角色",
        "permission_code": "USER_ROLE_ASSIGN",
        "resource": "user_role",
        "action": "assign",
        "description": "为用户分配角色",
        "is_active": True,
    },
    # 系统日志
    {
        "permission_name": "查看系统日志",
        "permission_code": "SYSTEM_LOG_VIEW",
        "resource": "system_log",
        "action": "view",
        "description": "查看系统日志记录",
        "is_active": True,
    },
]

DEFAULT_EXAMINATION_TYPES: List[Dict[str, object]] = [
    {
        "type_code": "FUNDUS_PHOTO",
        "type_name": "眼底照相",
        "description": "使用眼底相机拍摄眼底图像，用于观察视网膜、视神经、血管等结构",
        "body_part": "眼底",
        "duration_minutes": 15,
        "preparation_instructions": "检查前请勿使用散瞳剂，保持眼部清洁",
        "is_active": True,
    },
    {
        "type_code": "FFA",
        "type_name": "眼底血管造影",
        "description": "荧光素眼底血管造影检查，用于观察视网膜血管循环",
        "body_part": "眼底",
        "duration_minutes": 30,
        "preparation_instructions": "检查前4小时禁食，有碘过敏史请提前告知",
        "is_active": True,
    },
    {
        "type_code": "OCT",
        "type_name": "光学相干断层扫描",
        "description": "OCT检查，用于高分辨率观察视网膜结构，诊断黄斑病变等",
        "body_part": "眼底",
        "duration_minutes": 20,
        "preparation_instructions": "检查前请配合医生保持眼睛注视固定目标",
        "is_active": True,
    },
    {
        "type_code": "UWF",
        "type_name": "眼底广角照相",
        "description": "超广角眼底照相，可获取200度以上的眼底图像",
        "body_part": "眼底",
        "duration_minutes": 20,
        "preparation_instructions": "检查前需要散瞳，请安排好回程交通",
        "is_active": True,
    },
    {
        "type_code": "ICGA",
        "type_name": "吲哚菁绿血管造影",
        "description": "使用吲哚菁绿染料进行眼底血管造影，主要观察脉络膜循环",
        "body_part": "眼底",
        "duration_minutes": 35,
        "preparation_instructions": "检查前4小时禁食，有碘过敏史请提前告知",
        "is_active": True,
    },
]


def build_db_url(db_name: str) -> str:
    return (
        f"postgresql+psycopg://{POSTGRES_CONFIG['user']}:"
        f"{POSTGRES_CONFIG['password']}@{POSTGRES_CONFIG['host']}:"
        f"{POSTGRES_CONFIG['port']}/{db_name}"
    )


def ensure_database_exists() -> None:
    admin_engine = create_engine(build_db_url(DEFAULT_DB), isolation_level="AUTOCOMMIT")
    try:
        with admin_engine.connect() as connection:
            exists = connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                {"db_name": TARGET_DB},
            ).scalar()
            if not exists:
                connection.execute(text(f'CREATE DATABASE "{TARGET_DB}"'))
                print(f"✅ 已创建数据库 {TARGET_DB}")
            else:
                print(f"ℹ️ 数据库 {TARGET_DB} 已存在，跳过创建")
    finally:
        admin_engine.dispose()


def create_tables(engine: Engine) -> None:
    SQLModel.metadata.create_all(engine)
    print("✅ 已根据模型创建/更新所有数据表")


def init_admin_user(session: Session) -> User:
    admin_user = session.exec(
        select(User).where(User.username == DEFAULT_ADMIN_PROFILE["username"])
    ).first()
    if admin_user:
        print("ℹ️ 管理员账号已存在，跳过创建")
        return admin_user

    frontend_hash = hashlib.sha256(
        f"{DEFAULT_ADMIN_PASSWORD}{PASSWORD_SALT}".encode()
    ).hexdigest()
    password_hash = backend_hash_password(frontend_hash)

    admin_user = User(
        **DEFAULT_ADMIN_PROFILE,
        password_hash=password_hash,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    session.add(admin_user)
    session.flush()
    print(
        f"ℹ️ 管理员初始密码: {DEFAULT_ADMIN_PASSWORD} "
        f"(前端哈希: {frontend_hash})"
    )
    print("✅ 已创建管理员账号")
    return admin_user


def init_roles(session: Session) -> Dict[str, Role]:
    existing_roles = {
        role.role_code: role for role in session.exec(select(Role)).all()
    }
    for role_data in DEFAULT_ROLES:
        role_code = role_data["role_code"]
        if role_code in existing_roles:
            continue
        role = Role(**role_data, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
        session.add(role)
        session.flush()
        existing_roles[role_code] = role
        print(f"✅ 已创建角色 {role_code}")
    if not DEFAULT_ROLES:
        print("ℹ️ 无需创建角色")
    return existing_roles


def init_permissions(session: Session) -> Dict[str, Permission]:
    existing_permissions = {
        permission.permission_code: permission
        for permission in session.exec(select(Permission)).all()
    }
    for perm_data in DEFAULT_PERMISSIONS:
        perm_code = perm_data["permission_code"]
        if perm_code in existing_permissions:
            continue
        permission = Permission(
            **perm_data,
            created_at=datetime.utcnow(),
        )
        session.add(permission)
        session.flush()
        existing_permissions[perm_code] = permission
        print(f"✅ 已创建权限 {perm_code}")
    return existing_permissions


def init_examination_types(session: Session) -> None:
    existing_types = {
        exam.type_code: exam
        for exam in session.exec(select(ExaminationType)).all()
    }
    for exam_data in DEFAULT_EXAMINATION_TYPES:
        type_code = exam_data["type_code"]
        if type_code in existing_types:
            continue
        exam_type = ExaminationType(
            **exam_data,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(exam_type)
        session.flush()
        print(f"✅ 已创建检查类型 {type_code}")


def init_user_roles(session: Session, admin_user: User, admin_role: Role) -> None:
    if admin_user.id is None or admin_role.id is None:
        session.flush()
    exists = session.exec(
        select(UserRole).where(
            UserRole.user_id == admin_user.id,
            UserRole.role_id == admin_role.id,
        )
    ).first()
    if exists:
        print("ℹ️ 管理员角色已分配给管理员账号")
        return
    user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id, is_active=True)
    session.add(user_role)
    print("✅ 已为管理员账号分配管理员角色")


def init_role_permissions(
    session: Session, admin_role: Role, permissions: Iterable[Permission]
) -> None:
    existing_pairs = {
        (rp.role_id, rp.permission_id)
        for rp in session.exec(
            select(RolePermission).where(RolePermission.role_id == admin_role.id)
        ).all()
    }
    created_count = 0
    for permission in permissions:
        pair = (admin_role.id, permission.id)
        if pair in existing_pairs:
            continue
        role_perm = RolePermission(
            role_id=admin_role.id,
            permission_id=permission.id,
            is_active=True,
        )
        session.add(role_perm)
        created_count += 1
    if created_count:
        print(f"✅ 已为管理员角色新增 {created_count} 条权限关联")
    else:
        print("ℹ️ 管理员角色已拥有所有权限")


def init_database_data() -> None:
    ensure_database_exists()

    engine = create_engine(build_db_url(TARGET_DB))
    try:
        create_tables(engine)

        with Session(engine) as session:
            admin_user = init_admin_user(session)
            roles = init_roles(session)
            permissions = init_permissions(session)
            init_examination_types(session)

            admin_role = roles.get("ROLE_ADMIN")
            if not admin_role:
                raise RuntimeError("未找到 ROLE_ADMIN 角色，无法继续初始化")

            init_user_roles(session, admin_user, admin_role)
            init_role_permissions(session, admin_role, permissions.values())

            session.commit()
            print("🎉 数据初始化完成")
    except ProgrammingError as exc:
        print(f"❌ 数据库操作失败: {exc}")
        raise
    finally:
        engine.dispose()


if __name__ == "__main__":
    init_database_data()


