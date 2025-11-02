-- =============================================================================
-- 眼底影像管理系统 - 初始化数据脚本
-- =============================================================================
-- 说明：
-- 1. 本脚本用于初始化系统必需的基础数据
-- 2. 包含：默认管理员用户、默认角色、默认权限等
-- 3. 执行方式：psql -U postgres -d your_database -f init_data.sql
-- =============================================================================

BEGIN;

-- =============================================================================
-- 1. 创建默认管理员用户
-- =============================================================================
-- 注意：密码是 "admin123" 经过双重加密后的值
-- 前端SHA-256+盐值: a450a7646797889c78669d3b175a579ee85fc53717917975c32cb2becedf6598
-- 后端SHA-256+盐值: 07d04522a8d89670c146970172666d0849d368b46bbd7c3ee3c3f2b626cb0e2c
-- 盐值: eyes_remk_system_salt_change_in_production

INSERT INTO users (
    username,
    password_hash,
    email,
    phone,
    full_name,
    user_type,
    department,
    title,
    status,
    created_at,
    updated_at
)
VALUES (
    'admin',
    '07d04522a8d89670c146970172666d0849d368b46bbd7c3ee3c3f2b626cb0e2c',
    'admin@example.com',
    '13800138000',
    '系统管理员',
    'admin',
    '管理部',
    '系统管理员',
    'active',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
ON CONFLICT (username) DO NOTHING;

-- =============================================================================
-- 2. 创建测试医生账号（可选）
-- =============================================================================
-- 密码是 "doctor123"
-- 前端SHA-256+盐值: fb54717455a1b7698c1a33e2f731840a402c3285b73f461fa29a354fb8186a0c
-- 后端SHA-256+盐值: 0f3ff490d6e523955cbf5dc4a1a5f25bc7539f27fb6426a4ddf81e4005346fff
-- 盐值: eyes_remk_system_salt_change_in_production

INSERT INTO users (
    username,
    password_hash,
    email,
    phone,
    full_name,
    user_type,
    department,
    title,
    license_number,
    status,
    created_at,
    updated_at
)
VALUES (
    'doctor01',
    '0f3ff490d6e523955cbf5dc4a1a5f25bc7539f27fb6426a4ddf81e4005346fff',
    'doctor01@example.com',
    '13800138001',
    '张医生',
    'doctor',
    '眼科',
    '主治医师',
    'DOC2025001',
    'active',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
ON CONFLICT (username) DO NOTHING;

-- =============================================================================
-- 3. 创建默认角色
-- =============================================================================

INSERT INTO roles (
    role_name,
    role_code,
    description,
    is_system_role,
    is_active,
    created_at,
    updated_at
)
VALUES
    ('系统管理员', 'ROLE_ADMIN', '系统最高权限管理员', true, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('医生', 'ROLE_DOCTOR', '医生角色，可进行诊断和检查', true, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('技师', 'ROLE_TECHNICIAN', '技师角色，可操作设备和采集图像', true, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('查看者', 'ROLE_VIEWER', '只读权限，可查看数据但不能修改', true, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT (role_code) DO NOTHING;

-- =============================================================================
-- 4. 创建默认权限
-- =============================================================================

INSERT INTO permissions (
    permission_name,
    permission_code,
    resource,
    action,
    description,
    is_active,
    created_at,
    updated_at
)
VALUES
    -- 用户管理权限
    ('查看用户', 'USER_VIEW', 'user', 'view', '查看用户信息', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('创建用户', 'USER_CREATE', 'user', 'create', '创建新用户', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('编辑用户', 'USER_EDIT', 'user', 'edit', '编辑用户信息', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('删除用户', 'USER_DELETE', 'user', 'delete', '删除用户', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- 患者管理权限
    ('查看患者', 'PATIENT_VIEW', 'patient', 'view', '查看患者信息', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('创建患者', 'PATIENT_CREATE', 'patient', 'create', '创建患者档案', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('编辑患者', 'PATIENT_EDIT', 'patient', 'edit', '编辑患者信息', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('删除患者', 'PATIENT_DELETE', 'patient', 'delete', '删除患者档案', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- 检查管理权限
    ('查看检查', 'EXAMINATION_VIEW', 'examination', 'view', '查看检查记录', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('创建检查', 'EXAMINATION_CREATE', 'examination', 'create', '创建检查记录', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('编辑检查', 'EXAMINATION_EDIT', 'examination', 'edit', '编辑检查记录', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('删除检查', 'EXAMINATION_DELETE', 'examination', 'delete', '删除检查记录', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- 图像管理权限
    ('查看图像', 'IMAGE_VIEW', 'image', 'view', '查看眼底图像', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('上传图像', 'IMAGE_UPLOAD', 'image', 'upload', '上传眼底图像', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('删除图像', 'IMAGE_DELETE', 'image', 'delete', '删除眼底图像', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- 挂号管理权限
    ('查看挂号', 'REGISTRATION_VIEW', 'registration', 'view', '查看挂号信息', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('创建挂号', 'REGISTRATION_CREATE', 'registration', 'create', '创建挂号记录', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('编辑挂号', 'REGISTRATION_EDIT', 'registration', 'edit', '编辑挂号信息', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('删除挂号', 'REGISTRATION_DELETE', 'registration', 'delete', '删除挂号记录', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- 系统管理权限
    ('系统设置', 'SYSTEM_SETTINGS', 'system', 'settings', '系统设置管理', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('查看日志', 'SYSTEM_LOGS', 'system', 'logs', '查看系统日志', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('角色管理', 'ROLE_MANAGE', 'role', 'manage', '管理角色', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('权限管理', 'PERMISSION_MANAGE', 'permission', 'manage', '管理权限', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT (permission_code) DO NOTHING;

-- =============================================================================
-- 5. 分配用户角色
-- =============================================================================

-- 给管理员分配管理员角色
INSERT INTO user_roles (user_id, role_id, assigned_at, is_active)
SELECT 
    u.id,
    r.id,
    CURRENT_TIMESTAMP,
    true
FROM users u
CROSS JOIN roles r
WHERE u.username = 'admin'
  AND r.role_code = 'ROLE_ADMIN'
ON CONFLICT (user_id, role_id) DO NOTHING;

-- 给医生账号分配医生角色
INSERT INTO user_roles (user_id, role_id, assigned_at, is_active)
SELECT 
    u.id,
    r.id,
    CURRENT_TIMESTAMP,
    true
FROM users u
CROSS JOIN roles r
WHERE u.username = 'doctor01'
  AND r.role_code = 'ROLE_DOCTOR'
ON CONFLICT (user_id, role_id) DO NOTHING;

-- =============================================================================
-- 6. 分配角色权限
-- =============================================================================

-- 管理员角色：拥有所有权限
INSERT INTO role_permissions (role_id, permission_id, granted_at, is_active)
SELECT 
    r.id,
    p.id,
    CURRENT_TIMESTAMP,
    true
FROM roles r
CROSS JOIN permissions p
WHERE r.role_code = 'ROLE_ADMIN'
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- 医生角色：拥有查看和操作患者、检查、图像、挂号的权限
INSERT INTO role_permissions (role_id, permission_id, granted_at, is_active)
SELECT 
    r.id,
    p.id,
    CURRENT_TIMESTAMP,
    true
FROM roles r
CROSS JOIN permissions p
WHERE r.role_code = 'ROLE_DOCTOR'
  AND p.permission_code IN (
    'PATIENT_VIEW', 'PATIENT_CREATE', 'PATIENT_EDIT',
    'EXAMINATION_VIEW', 'EXAMINATION_CREATE', 'EXAMINATION_EDIT',
    'IMAGE_VIEW', 'IMAGE_UPLOAD',
    'REGISTRATION_VIEW', 'REGISTRATION_CREATE', 'REGISTRATION_EDIT'
  )
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- 技师角色：拥有查看和操作检查、图像的权限
INSERT INTO role_permissions (role_id, permission_id, granted_at, is_active)
SELECT 
    r.id,
    p.id,
    CURRENT_TIMESTAMP,
    true
FROM roles r
CROSS JOIN permissions p
WHERE r.role_code = 'ROLE_TECHNICIAN'
  AND p.permission_code IN (
    'PATIENT_VIEW',
    'EXAMINATION_VIEW',
    'IMAGE_VIEW', 'IMAGE_UPLOAD',
    'REGISTRATION_VIEW'
  )
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- 查看者角色：只有查看权限
INSERT INTO role_permissions (role_id, permission_id, granted_at, is_active)
SELECT 
    r.id,
    p.id,
    CURRENT_TIMESTAMP,
    true
FROM roles r
CROSS JOIN permissions p
WHERE r.role_code = 'ROLE_VIEWER'
  AND p.permission_code LIKE '%_VIEW'
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- =============================================================================
-- 7. 创建默认检查类型（可选）
-- =============================================================================

INSERT INTO examination_types (
    type_name,
    type_code,
    description,
    duration_minutes,
    is_active,
    created_at,
    updated_at
)
VALUES
    ('眼底照相', 'FUNDUS_PHOTO', '使用眼底相机拍摄眼底图像', 15, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('眼底血管造影', 'FFA', '荧光素眼底血管造影检查', 30, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('光学相干断层扫描', 'OCT', 'OCT检查，用于观察视网膜结构', 20, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('眼底广角照相', 'UWF', '超广角眼底照相', 20, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT (type_code) DO NOTHING;

-- =============================================================================
-- 完成提示
-- =============================================================================

COMMIT;

-- 显示初始化结果
SELECT 
    '初始化完成!' as message,
    (SELECT COUNT(*) FROM users WHERE deleted_at IS NULL) as user_count,
    (SELECT COUNT(*) FROM roles WHERE deleted_at IS NULL) as role_count,
    (SELECT COUNT(*) FROM permissions WHERE deleted_at IS NULL) as permission_count;

-- 显示默认账号信息
SELECT 
    '默认账号' as info_type,
    username as 用户名,
    '见文档' as 密码,
    user_type as 用户类型,
    full_name as 姓名,
    status as 状态
FROM users 
WHERE username IN ('admin', 'doctor01')
  AND deleted_at IS NULL;

