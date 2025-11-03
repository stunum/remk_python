-- =============================================================================
-- 眼底影像管理系统 - 初始化数据脚本
-- =============================================================================
-- 说明：
-- 1. 本脚本用于初始化系统必需的基础数据
-- 2. 包含：默认用户（管理员/医生/技师/查看者）、默认角色、默认权限、检查类型等
-- 3. 执行方式：psql -U postgres -d your_database -f init_data.sql
-- 4. 可重复执行：使用 ON CONFLICT 和条件 INSERT 避免重复数据
-- =============================================================================

BEGIN;

-- =============================================================================
-- 1. 创建默认用户账号
-- =============================================================================

-- 1.1 系统管理员账号
-- 用户名: admin
-- 密码: admin123
-- 前端SHA-256哈希: 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9
-- 后端SHA-256+盐值哈希: 1a60d0a84a9c284169f2602fe9f38ca06b0166697feafe2f9e1eb01fa4a61f21
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
    'admin@eyesremk.com',
    '13800000000',
    '系统管理员',
    'admin',
    '管理部',
    '系统管理员',
    'active',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
ON CONFLICT (username) DO NOTHING;

-- 1.2 测试医生账号
-- 用户名: doctor01
-- 密码: doctor123
-- 前端SHA-256哈希: f348d5628621f3d8f59c8cabda0f8eb0aa7e0514a90be7571020b1336f26c113
-- 后端SHA-256+盐值哈希: cebc83396a6515e166bbf6baecaf1e6d9ed46a48dec9dedad0598cc1d8a3b920

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
    'cebc83396a6515e166bbf6baecaf1e6d9ed46a48dec9dedad0598cc1d8a3b920',
    'doctor01@eyesremk.com',
    '13800000001',
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

-- 1.3 测试技师账号
-- 用户名: technician01
-- 密码: technician123
-- 前端SHA-256哈希: f6bd91ad17bea2a88d6e3ff462d500b777d5114fe6066659faa07399f7c5d967
-- 后端SHA-256+盐值哈希: 0d00e5d716753c55087734394a9c0c9dbdf6f71c32285e60582a7a86fe94d538

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
    'technician01',
    '0d00e5d716753c55087734394a9c0c9dbdf6f71c32285e60582a7a86fe94d538',
    'technician01@eyesremk.com',
    '13800000002',
    '李技师',
    'technician',
    '眼科检查室',
    '检查技师',
    'active',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
ON CONFLICT (username) DO NOTHING;

-- 1.4 测试查看者账号
-- 用户名: viewer01
-- 密码: viewer123
-- 前端SHA-256哈希: 65375049b9e4d7cad6c9ba286fdeb9394b28135a3e84136404cfccfdcc438894
-- 后端SHA-256+盐值哈希: 208c405c283336c77de7771b4098d4a4da9244de8d6962d01f226abb6478fcfa

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
    'viewer01',
    '208c405c283336c77de7771b4098d4a4da9244de8d6962d01f226abb6478fcfa',
    'viewer01@eyesremk.com',
    '13800000003',
    '王查看员',
    'viewer',
    '信息科',
    '数据查看员',
    'active',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
ON CONFLICT (username) DO NOTHING;

-- =============================================================================
-- 2. 创建默认角色
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
    ('系统管理员', 'ROLE_ADMIN', '系统最高权限管理员，拥有所有权限', true, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('医生', 'ROLE_DOCTOR', '医生角色，可进行诊断、检查、患者管理等操作', true, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('技师', 'ROLE_TECHNICIAN', '技师角色，可操作设备、采集图像、查看患者信息', true, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('查看者', 'ROLE_VIEWER', '只读权限，可查看数据但不能修改', true, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT (role_code) DO NOTHING;

-- =============================================================================
-- 3. 创建默认权限
-- =============================================================================

INSERT INTO permissions (
    permission_name,
    permission_code,
    resource,
    action,
    description,
    is_active,
    created_at
)
VALUES
    -- 用户管理权限
    ('查看用户', 'USER_VIEW', 'user', 'view', '查看用户信息', true, CURRENT_TIMESTAMP),
    ('创建用户', 'USER_CREATE', 'user', 'create', '创建新用户', true, CURRENT_TIMESTAMP),
    ('编辑用户', 'USER_EDIT', 'user', 'edit', '编辑用户信息', true, CURRENT_TIMESTAMP),
    ('删除用户', 'USER_DELETE', 'user', 'delete', '删除用户', true, CURRENT_TIMESTAMP),
    
    -- 患者管理权限
    ('查看患者', 'PATIENT_VIEW', 'patient', 'view', '查看患者信息', true, CURRENT_TIMESTAMP),
    ('创建患者', 'PATIENT_CREATE', 'patient', 'create', '创建患者档案', true, CURRENT_TIMESTAMP),
    ('编辑患者', 'PATIENT_EDIT', 'patient', 'edit', '编辑患者信息', true, CURRENT_TIMESTAMP),
    ('删除患者', 'PATIENT_DELETE', 'patient', 'delete', '删除患者档案', true, CURRENT_TIMESTAMP),
    
    -- 检查管理权限
    ('查看检查', 'EXAMINATION_VIEW', 'examination', 'view', '查看检查记录', true, CURRENT_TIMESTAMP),
    ('创建检查', 'EXAMINATION_CREATE', 'examination', 'create', '创建检查记录', true, CURRENT_TIMESTAMP),
    ('编辑检查', 'EXAMINATION_EDIT', 'examination', 'edit', '编辑检查记录', true, CURRENT_TIMESTAMP),
    ('删除检查', 'EXAMINATION_DELETE', 'examination', 'delete', '删除检查记录', true, CURRENT_TIMESTAMP),
    
    -- 图像管理权限
    ('查看图像', 'IMAGE_VIEW', 'image', 'view', '查看眼底图像', true, CURRENT_TIMESTAMP),
    ('上传图像', 'IMAGE_UPLOAD', 'image', 'upload', '上传眼底图像', true, CURRENT_TIMESTAMP),
    ('删除图像', 'IMAGE_DELETE', 'image', 'delete', '删除眼底图像', true, CURRENT_TIMESTAMP),
    
    -- 挂号管理权限
    ('查看挂号', 'REGISTRATION_VIEW', 'registration', 'view', '查看挂号信息', true, CURRENT_TIMESTAMP),
    ('创建挂号', 'REGISTRATION_CREATE', 'registration', 'create', '创建挂号记录', true, CURRENT_TIMESTAMP),
    ('编辑挂号', 'REGISTRATION_EDIT', 'registration', 'edit', '编辑挂号信息', true, CURRENT_TIMESTAMP),
    ('删除挂号', 'REGISTRATION_DELETE', 'registration', 'delete', '删除挂号记录', true, CURRENT_TIMESTAMP),
    
    -- 诊断管理权限
    ('查看诊断', 'DIAGNOSIS_VIEW', 'diagnosis', 'view', '查看诊断记录', true, CURRENT_TIMESTAMP),
    ('创建诊断', 'DIAGNOSIS_CREATE', 'diagnosis', 'create', '创建诊断记录', true, CURRENT_TIMESTAMP),
    ('编辑诊断', 'DIAGNOSIS_EDIT', 'diagnosis', 'edit', '编辑诊断记录', true, CURRENT_TIMESTAMP),
    ('删除诊断', 'DIAGNOSIS_DELETE', 'diagnosis', 'delete', '删除诊断记录', true, CURRENT_TIMESTAMP),
    
    -- 随访管理权限
    ('查看随访', 'FOLLOWUP_VIEW', 'followup', 'view', '查看随访计划', true, CURRENT_TIMESTAMP),
    ('创建随访', 'FOLLOWUP_CREATE', 'followup', 'create', '创建随访计划', true, CURRENT_TIMESTAMP),
    ('编辑随访', 'FOLLOWUP_EDIT', 'followup', 'edit', '编辑随访计划', true, CURRENT_TIMESTAMP),
    ('删除随访', 'FOLLOWUP_DELETE', 'followup', 'delete', '删除随访计划', true, CURRENT_TIMESTAMP),
    
    -- 系统管理权限
    ('系统设置', 'SYSTEM_SETTINGS', 'system', 'settings', '系统设置管理', true, CURRENT_TIMESTAMP),
    ('查看日志', 'SYSTEM_LOGS', 'system', 'logs', '查看系统日志', true, CURRENT_TIMESTAMP),
    ('角色管理', 'ROLE_MANAGE', 'role', 'manage', '管理角色', true, CURRENT_TIMESTAMP),
    ('权限管理', 'PERMISSION_MANAGE', 'permission', 'manage', '管理权限', true, CURRENT_TIMESTAMP)
ON CONFLICT (permission_code) DO NOTHING;

-- =============================================================================
-- 4. 分配用户角色 - 使用条件插入避免重复
-- =============================================================================

-- 4.1 给管理员分配管理员角色
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
  AND u.deleted_at IS NULL
  AND r.deleted_at IS NULL
  AND NOT EXISTS (
    SELECT 1 FROM user_roles ur 
    WHERE ur.user_id = u.id 
      AND ur.role_id = r.id 
      AND ur.deleted_at IS NULL
  );

-- 4.2 给医生账号分配医生角色
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
  AND u.deleted_at IS NULL
  AND r.deleted_at IS NULL
  AND NOT EXISTS (
    SELECT 1 FROM user_roles ur 
    WHERE ur.user_id = u.id 
      AND ur.role_id = r.id 
      AND ur.deleted_at IS NULL
  );

-- 4.3 给技师账号分配技师角色
INSERT INTO user_roles (user_id, role_id, assigned_at, is_active)
SELECT 
    u.id,
    r.id,
    CURRENT_TIMESTAMP,
    true
FROM users u
CROSS JOIN roles r
WHERE u.username = 'technician01'
  AND r.role_code = 'ROLE_TECHNICIAN'
  AND u.deleted_at IS NULL
  AND r.deleted_at IS NULL
  AND NOT EXISTS (
    SELECT 1 FROM user_roles ur 
    WHERE ur.user_id = u.id 
      AND ur.role_id = r.id 
      AND ur.deleted_at IS NULL
  );

-- 4.4 给查看者账号分配查看者角色
INSERT INTO user_roles (user_id, role_id, assigned_at, is_active)
SELECT 
    u.id,
    r.id,
    CURRENT_TIMESTAMP,
    true
FROM users u
CROSS JOIN roles r
WHERE u.username = 'viewer01'
  AND r.role_code = 'ROLE_VIEWER'
  AND u.deleted_at IS NULL
  AND r.deleted_at IS NULL
  AND NOT EXISTS (
    SELECT 1 FROM user_roles ur 
    WHERE ur.user_id = u.id 
      AND ur.role_id = r.id 
      AND ur.deleted_at IS NULL
  );

-- =============================================================================
-- 5. 分配角色权限 - 使用条件插入避免重复
-- =============================================================================

-- 5.1 管理员角色：拥有所有权限
INSERT INTO role_permissions (role_id, permission_id, granted_at, is_active)
SELECT 
    r.id,
    p.id,
    CURRENT_TIMESTAMP,
    true
FROM roles r
CROSS JOIN permissions p
WHERE r.role_code = 'ROLE_ADMIN'
  AND r.deleted_at IS NULL
  AND p.deleted_at IS NULL
  AND NOT EXISTS (
    SELECT 1 FROM role_permissions rp 
    WHERE rp.role_id = r.id 
      AND rp.permission_id = p.id 
      AND rp.deleted_at IS NULL
  );

-- 5.2 医生角色：拥有患者、检查、图像、挂号、诊断、随访的完整权限
INSERT INTO role_permissions (role_id, permission_id, granted_at, is_active)
SELECT 
    r.id,
    p.id,
    CURRENT_TIMESTAMP,
    true
FROM roles r
CROSS JOIN permissions p
WHERE r.role_code = 'ROLE_DOCTOR'
  AND r.deleted_at IS NULL
  AND p.deleted_at IS NULL
  AND p.permission_code IN (
    'PATIENT_VIEW', 'PATIENT_CREATE', 'PATIENT_EDIT',
    'EXAMINATION_VIEW', 'EXAMINATION_CREATE', 'EXAMINATION_EDIT',
    'IMAGE_VIEW', 'IMAGE_UPLOAD',
    'REGISTRATION_VIEW', 'REGISTRATION_CREATE', 'REGISTRATION_EDIT',
    'DIAGNOSIS_VIEW', 'DIAGNOSIS_CREATE', 'DIAGNOSIS_EDIT',
    'FOLLOWUP_VIEW', 'FOLLOWUP_CREATE', 'FOLLOWUP_EDIT'
  )
  AND NOT EXISTS (
    SELECT 1 FROM role_permissions rp 
    WHERE rp.role_id = r.id 
      AND rp.permission_id = p.id 
      AND rp.deleted_at IS NULL
  );

-- 5.3 技师角色：拥有查看患者、检查和操作图像的权限
INSERT INTO role_permissions (role_id, permission_id, granted_at, is_active)
SELECT 
    r.id,
    p.id,
    CURRENT_TIMESTAMP,
    true
FROM roles r
CROSS JOIN permissions p
WHERE r.role_code = 'ROLE_TECHNICIAN'
  AND r.deleted_at IS NULL
  AND p.deleted_at IS NULL
  AND p.permission_code IN (
    'PATIENT_VIEW',
    'EXAMINATION_VIEW',
    'IMAGE_VIEW', 'IMAGE_UPLOAD',
    'REGISTRATION_VIEW'
  )
  AND NOT EXISTS (
    SELECT 1 FROM role_permissions rp 
    WHERE rp.role_id = r.id 
      AND rp.permission_id = p.id 
      AND rp.deleted_at IS NULL
  );

-- 5.4 查看者角色：只有查看权限
INSERT INTO role_permissions (role_id, permission_id, granted_at, is_active)
SELECT 
    r.id,
    p.id,
    CURRENT_TIMESTAMP,
    true
FROM roles r
CROSS JOIN permissions p
WHERE r.role_code = 'ROLE_VIEWER'
  AND r.deleted_at IS NULL
  AND p.deleted_at IS NULL
  AND p.permission_code LIKE '%_VIEW'
  AND NOT EXISTS (
    SELECT 1 FROM role_permissions rp 
    WHERE rp.role_id = r.id 
      AND rp.permission_id = p.id 
      AND rp.deleted_at IS NULL
  );

-- =============================================================================
-- 6. 创建默认检查类型
-- =============================================================================

INSERT INTO examination_types (
    type_code,
    type_name,
    description,
    body_part,
    duration_minutes,
    preparation_instructions,
    is_active,
    created_at,
    updated_at
)
VALUES
    ('FUNDUS_PHOTO', '眼底照相', '使用眼底相机拍摄眼底图像，用于观察视网膜、视神经、血管等结构', '眼底', 15, '检查前请勿使用散瞳剂，保持眼部清洁', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('FFA', '眼底血管造影', '荧光素眼底血管造影检查，用于观察视网膜血管循环', '眼底', 30, '检查前4小时禁食，有碘过敏史请提前告知', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('OCT', '光学相干断层扫描', 'OCT检查，用于高分辨率观察视网膜结构，诊断黄斑病变等', '眼底', 20, '检查前请配合医生保持眼睛注视固定目标', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('UWF', '眼底广角照相', '超广角眼底照相，可获取200度以上的眼底图像', '眼底', 20, '检查前需要散瞳，请安排好回程交通', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('ICGA', '吲哚菁绿血管造影', '使用吲哚菁绿染料进行眼底血管造影，主要观察脉络膜循环', '眼底', 35, '检查前4小时禁食，有碘过敏史请提前告知', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT (type_code) DO NOTHING;

-- =============================================================================
-- 7. 创建示例患者数据（可选）
-- =============================================================================

INSERT INTO patients (
    patient_id,
    name,
    gender,
    birth_date,
    phone,
    email,
    address,
    medical_history,
    allergies,
    status,
    created_at,
    updated_at
)
VALUES
    ('P2025000001', '张三', 'male', '1985-06-15', '13900000001', 'zhangsan@example.com', '北京市朝阳区示例街道1号', '高血压病史5年', '无已知药物过敏', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('P2025000002', '李四', 'female', '1990-03-20', '13900000002', 'lisi@example.com', '北京市海淀区示例路2号', '糖尿病病史3年', '青霉素过敏', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('P2025000003', '王五', 'male', '1978-11-08', '13900000003', 'wangwu@example.com', '北京市西城区示例胡同3号', '无特殊病史', '无已知药物过敏', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT (patient_id) DO NOTHING;

-- =============================================================================
-- 完成提示
-- =============================================================================

COMMIT;

-- 显示初始化结果
SELECT 
    '✅ 初始化完成!' as message,
    (SELECT COUNT(*) FROM users WHERE deleted_at IS NULL) as 用户数量,
    (SELECT COUNT(*) FROM roles WHERE deleted_at IS NULL) as 角色数量,
    (SELECT COUNT(*) FROM permissions WHERE deleted_at IS NULL) as 权限数量,
    (SELECT COUNT(*) FROM user_roles WHERE deleted_at IS NULL) as 用户角色关联数,
    (SELECT COUNT(*) FROM role_permissions WHERE deleted_at IS NULL) as 角色权限关联数,
    (SELECT COUNT(*) FROM examination_types WHERE deleted_at IS NULL) as 检查类型数量,
    (SELECT COUNT(*) FROM patients WHERE deleted_at IS NULL) as 患者数量;

-- 显示默认账号信息
SELECT 
    '📋 默认账号信息' as 说明,
    username as 用户名,
    CASE username
        WHEN 'admin' THEN 'admin123'
        WHEN 'doctor01' THEN 'doctor123'
        WHEN 'technician01' THEN 'technician123'
        WHEN 'viewer01' THEN 'viewer123'
    END as 密码,
    user_type as 用户类型,
    full_name as 姓名,
    email as 邮箱,
    status as 状态
FROM users 
WHERE username IN ('admin', 'doctor01', 'technician01', 'viewer01')
  AND deleted_at IS NULL
ORDER BY 
    CASE user_type
        WHEN 'admin' THEN 1
        WHEN 'doctor' THEN 2
        WHEN 'technician' THEN 3
        WHEN 'viewer' THEN 4
    END;

-- =============================================================================
-- 登录测试说明
-- =============================================================================

-- 使用以下信息进行登录测试：
--
-- 1. 管理员账号
--    用户名: admin
--    密码（原始）: admin123
--    密码（前端SHA-256）: 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9
--
-- 2. 医生账号
--    用户名: doctor01
--    密码（原始）: doctor123
--    密码（前端SHA-256）: f348d5628621f3d8f59c8cabda0f8eb0aa7e0514a90be7571020b1336f26c113
--
-- 3. 技师账号
--    用户名: technician01
--    密码（原始）: technician123
--    密码（前端SHA-256）: f6bd91ad17bea2a88d6e3ff462d500b777d5114fe6066659faa07399f7c5d967
--
-- 4. 查看者账号
--    用户名: viewer01
--    密码（原始）: viewer123
--    密码（前端SHA-256）: 65375049b9e4d7cad6c9ba286fdeb9394b28135a3e84136404cfccfdcc438894
--
-- 登录API测试命令（示例 - 管理员）：
--   curl -X POST "http://localhost:8000/api/auth/login" \
--     -H "Content-Type: application/json" \
--     -d '{
--       "username": "admin",
--       "password": "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"
--     }'
--
-- =============================================================================
