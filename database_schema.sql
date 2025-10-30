-- 眼底数据库系统初始化脚本(可重复执行)
-- 包含时区支持、软删除、一致性字段命名、索引优化等特性

BEGIN;

-- 清理旧对象(按依赖顺序)
DROP TABLE IF EXISTS system_logs CASCADE;
DROP TABLE IF EXISTS role_permissions CASCADE;
DROP TABLE IF EXISTS user_roles CASCADE;
DROP TABLE IF EXISTS permissions CASCADE;
DROP TABLE IF EXISTS roles CASCADE;
DROP TABLE IF EXISTS follow_ups CASCADE;
DROP TABLE IF EXISTS diagnosis_records CASCADE;
DROP TABLE IF EXISTS ai_diagnoses CASCADE;
DROP TABLE IF EXISTS fundus_images CASCADE;
DROP TABLE IF EXISTS examinations CASCADE;
DROP TABLE IF EXISTS registrations CASCADE;
DROP TABLE IF EXISTS examination_types CASCADE;
DROP TABLE IF EXISTS patients CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- 1. 用户/医生信息管理表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,                                     -- 用户ID
    username VARCHAR(50) NOT NULL UNIQUE,                     -- 用户名
    password_hash VARCHAR(255) NOT NULL,                      -- 密码哈希
    email VARCHAR(100) UNIQUE,                                -- 邮箱
    phone VARCHAR(20),                                        -- 电话号码
    full_name VARCHAR(100) NOT NULL,                          -- 姓名
    user_type VARCHAR(20) NOT NULL DEFAULT 'doctor' CHECK (user_type IN ('admin', 'doctor', 'technician', 'viewer')),  -- 用户类型
    department VARCHAR(100),                                  -- 科室
    title VARCHAR(50),                                        -- 职称
    license_number VARCHAR(50),                               -- 执业证书号
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'locked')),  -- 状态
    last_login_at TIMESTAMPTZ,                                -- 最后登录时间(带时区)
    deleted_at TIMESTAMPTZ,                                   -- 软删除时间戳(带时区)
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,         -- 创建时间(带时区)
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,         -- 更新时间(带时区)
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL, -- 创建人
    updated_by INTEGER REFERENCES users(id) ON DELETE SET NULL  -- 更新人
);
COMMENT ON TABLE users IS '用户信息表:管理系统中所有用户(医生、技师、管理员等)的基本信息';
COMMENT ON COLUMN users.id IS '用户ID';
COMMENT ON COLUMN users.username IS '用户名';
COMMENT ON COLUMN users.password_hash IS '密码哈希';
COMMENT ON COLUMN users.email IS '邮箱';
COMMENT ON COLUMN users.phone IS '电话号码';
COMMENT ON COLUMN users.full_name IS '姓名';
COMMENT ON COLUMN users.user_type IS '用户类型:管理员/医生/技师/查看者';
COMMENT ON COLUMN users.department IS '科室';
COMMENT ON COLUMN users.title IS '职称';
COMMENT ON COLUMN users.license_number IS '执业证书号';
COMMENT ON COLUMN users.status IS '状态:激活/非激活/锁定';
COMMENT ON COLUMN users.last_login_at IS '最后登录时间(带时区)';
COMMENT ON COLUMN users.deleted_at IS '软删除时间戳(带时区)';
COMMENT ON COLUMN users.created_at IS '创建时间(带时区)';
COMMENT ON COLUMN users.updated_at IS '更新时间(带时区)';
COMMENT ON COLUMN users.created_by IS '创建人';
COMMENT ON COLUMN users.updated_by IS '更新人';

-- 2. 患者信息管理表
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,                                     -- 患者内部ID
    patient_id VARCHAR(50) NOT NULL UNIQUE,                   -- 患者编号
    name VARCHAR(100) NOT NULL,                               -- 患者姓名
    gender VARCHAR(10) CHECK (gender IN ('male', 'female', 'other')),  -- 性别
    birth_date DATE,                                         -- 出生日期
    phone VARCHAR(20),                                       -- 联系电话
    email VARCHAR(100),                                      -- 邮箱
    address TEXT,                                            -- 地址
    emergency_contact VARCHAR(100),                          -- 紧急联系人
    emergency_phone VARCHAR(20),                             -- 紧急联系人电话
    medical_history TEXT,                                    -- 病史
    allergies TEXT,                                          -- 过敏史
    current_medications TEXT,                                -- 当前用药
    insurance_info JSONB,                                    -- 医保信息(JSON 格式)
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'deceased')),  -- 状态
    deleted_at TIMESTAMPTZ,                                   -- 软删除时间戳(带时区)
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,          -- 创建时间(带时区)
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,          -- 更新时间(带时区)
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL, -- 创建人
    updated_by INTEGER REFERENCES users(id) ON DELETE SET NULL  -- 更新人
);
COMMENT ON TABLE patients IS '患者信息表:存储患者的基本信息和医疗背景';
COMMENT ON COLUMN patients.id IS '患者内部ID';
COMMENT ON COLUMN patients.patient_id IS '患者编号';
COMMENT ON COLUMN patients.name IS '患者姓名';
COMMENT ON COLUMN patients.gender IS '性别';
COMMENT ON COLUMN patients.birth_date IS '出生日期';
COMMENT ON COLUMN patients.phone IS '联系电话';
COMMENT ON COLUMN patients.email IS '邮箱';
COMMENT ON COLUMN patients.address IS '地址';
COMMENT ON COLUMN patients.emergency_contact IS '紧急联系人';
COMMENT ON COLUMN patients.emergency_phone IS '紧急联系人电话';
COMMENT ON COLUMN patients.medical_history IS '病史';
COMMENT ON COLUMN patients.allergies IS '过敏史';
COMMENT ON COLUMN patients.current_medications IS '当前用药';
COMMENT ON COLUMN patients.insurance_info IS '医保信息';
COMMENT ON COLUMN patients.status IS '状态:激活/非激活/已故';
COMMENT ON COLUMN patients.deleted_at IS '软删除时间戳(带时区)';
COMMENT ON COLUMN patients.created_at IS '创建时间(带时区)';
COMMENT ON COLUMN patients.updated_at IS '更新时间(带时区)';
COMMENT ON COLUMN patients.created_by IS '创建人';
COMMENT ON COLUMN patients.updated_by IS '更新人';

-- 3. 检查类型管理表
CREATE TABLE examination_types (
    id SERIAL PRIMARY KEY,                                     -- 类型ID
    type_code VARCHAR(20) NOT NULL UNIQUE,                    -- 检查类型代码
    type_name VARCHAR(100) NOT NULL,                          -- 检查类型名称
    description TEXT,                                         -- 检查描述
    body_part VARCHAR(50),                                    -- 检查部位
    duration_minutes INTEGER CHECK (duration_minutes >= 0),   -- 预计检查时长(分钟)
    preparation_instructions TEXT,                            -- 检查前准备说明
    is_active BOOLEAN DEFAULT true,                           -- 是否启用
    deleted_at TIMESTAMPTZ,                                   -- 软删除时间戳(带时区)
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,           -- 创建时间(带时区)
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP            -- 更新时间(带时区)
);
COMMENT ON TABLE examination_types IS '检查类型表:定义不同类型的眼底检查项目';
COMMENT ON COLUMN examination_types.id IS '类型ID';
COMMENT ON COLUMN examination_types.type_code IS '检查类型代码';
COMMENT ON COLUMN examination_types.type_name IS '检查类型名称';
COMMENT ON COLUMN examination_types.description IS '检查描述';
COMMENT ON COLUMN examination_types.body_part IS '检查部位';
COMMENT ON COLUMN examination_types.duration_minutes IS '预计检查时长(分钟)';
COMMENT ON COLUMN examination_types.preparation_instructions IS '检查前准备说明';
COMMENT ON COLUMN examination_types.is_active IS '是否启用';
COMMENT ON COLUMN examination_types.deleted_at IS '软删除时间戳(带时区)';
COMMENT ON COLUMN examination_types.created_at IS '创建时间(带时区)';
COMMENT ON COLUMN examination_types.updated_at IS '更新时间(带时区)';

-- 4. 检查记录表(可独立存在，也可与挂号关联)
CREATE TABLE examinations (
    id SERIAL PRIMARY KEY,                                     -- 检查记录ID
    examination_number VARCHAR(50) NOT NULL UNIQUE,           -- 检查编号
    patient_id INTEGER NOT NULL REFERENCES patients(id),       -- 患者ID
    examination_type_id INTEGER NOT NULL REFERENCES examination_types(id),  -- 检查类型ID
    doctor_id INTEGER REFERENCES users(id) ON DELETE SET NULL,-- 主治医生ID
    technician_id INTEGER REFERENCES users(id) ON DELETE SET NULL, -- 检查技师ID
    examination_date DATE NOT NULL,                            -- 检查日期
    examination_time TIME,                                     -- 检查时间
    eye_side VARCHAR(10) CHECK (eye_side IN ('left', 'right', 'both')),  -- 检查眼别
    chief_complaint TEXT,                                      -- 主诉
    present_illness TEXT,                                     -- 现病史
    examination_findings TEXT,                                -- 检查所见
    preliminary_diagnosis TEXT,                               -- 初步诊断
    recommendations TEXT,                                     -- 建议
    follow_up_date DATE,                                      -- 随访日期
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),  -- 状态
    notes TEXT,                                               -- 备注
    deleted_at TIMESTAMPTZ,                                   -- 软删除时间戳(带时区)
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,           -- 创建时间(带时区)
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,           -- 更新时间(带时区)
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,-- 创建人
    updated_by INTEGER REFERENCES users(id) ON DELETE SET NULL -- 更新人
);
COMMENT ON TABLE examinations IS '检查记录表:记录每次眼底检查的基本信息和结果(可独立存在或与挂号关联)';
COMMENT ON COLUMN examinations.id IS '检查记录ID';
COMMENT ON COLUMN examinations.examination_number IS '检查编号';
COMMENT ON COLUMN examinations.patient_id IS '患者ID';
COMMENT ON COLUMN examinations.examination_type_id IS '检查类型ID';
COMMENT ON COLUMN examinations.doctor_id IS '主治医生ID';
COMMENT ON COLUMN examinations.technician_id IS '检查技师ID';
COMMENT ON COLUMN examinations.examination_date IS '检查日期';
COMMENT ON COLUMN examinations.examination_time IS '检查时间';
COMMENT ON COLUMN examinations.eye_side IS '检查眼别:左眼/右眼/双眼';
COMMENT ON COLUMN examinations.chief_complaint IS '主诉';
COMMENT ON COLUMN examinations.present_illness IS '现病史';
COMMENT ON COLUMN examinations.examination_findings IS '检查所见';
COMMENT ON COLUMN examinations.preliminary_diagnosis IS '初步诊断';
COMMENT ON COLUMN examinations.recommendations IS '建议';
COMMENT ON COLUMN examinations.follow_up_date IS '随访日期';
COMMENT ON COLUMN examinations.status IS '状态:待检查/检查中/已完成/已取消';
COMMENT ON COLUMN examinations.notes IS '备注';
COMMENT ON COLUMN examinations.deleted_at IS '软删除时间戳(带时区)';
COMMENT ON COLUMN examinations.created_at IS '创建时间(带时区)';
COMMENT ON COLUMN examinations.updated_at IS '更新时间(带时区)';
COMMENT ON COLUMN examinations.created_by IS '创建人';
COMMENT ON COLUMN examinations.updated_by IS '更新人';

-- 4.1 挂号登记表(新增)
CREATE TABLE registrations (
    id SERIAL PRIMARY KEY,                                     -- 挂号ID
    registration_number VARCHAR(50) NOT NULL UNIQUE,           -- 挂号编号(全局唯一，不作为队列号)
    patient_id INTEGER NOT NULL REFERENCES patients(id),       -- 患者ID
    examination_type_id INTEGER NOT NULL REFERENCES examination_types(id),  -- 检查类型ID
    doctor_id INTEGER REFERENCES users(id) ON DELETE SET NULL, -- 医生ID
    examination_id INTEGER REFERENCES examinations(id) ON DELETE SET NULL, -- 检查记录ID(与examinations一对一关联，可选)
    department VARCHAR(100),                                   -- 科室
    registration_date DATE NOT NULL,                           -- 挂号日期
    registration_time TIME,                                    -- 挂号时间
    scheduled_date DATE NOT NULL,                              -- 预约检查日期
    scheduled_time TIME,                                       -- 预约检查时间
    priority VARCHAR(20) DEFAULT 'normal' CHECK (priority IN ('urgent', 'high', 'normal', 'low')),  -- 优先级
    registration_type VARCHAR(20) DEFAULT 'normal' CHECK (registration_type IN ('emergency', 'appointment', 'normal', 'followup')),  -- 挂号类型
    status VARCHAR(20) NOT NULL DEFAULT 'unsigned' CHECK (status IN ('unsigned','checked_in', 'cancelled')),  -- 挂号状态(含未签到)
    registration_fee DECIMAL(10,2) CHECK (registration_fee >= 0),                            -- 挂号费
    payment_status VARCHAR(20) DEFAULT 'unpaid' CHECK (payment_status IN ('unpaid', 'paid', 'refunded')),  -- 缴费状态
    payment_method VARCHAR(20),                                -- 支付方式
    chief_complaint TEXT,                                      -- 主诉
    present_illness TEXT,                                      -- 现病史
    referral_doctor VARCHAR(100),                              -- 转诊医生
    referral_hospital VARCHAR(200),                            -- 转诊医院
    notes TEXT,                                                -- 备注
    check_in_time TIMESTAMPTZ,                                 -- 签到时间
    queue_number INTEGER CHECK (queue_number >= 0),                                      -- 排队号码(当天/当科室内序号)
    estimated_wait_time INTEGER CHECK (estimated_wait_time >= 0),                               -- 预计等待时间(分钟)
    deleted_at TIMESTAMPTZ,                                    -- 软删除时间戳(带时区)
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,          -- 创建时间(带时区)
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,          -- 更新时间(带时区)
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,-- 创建人
    updated_by INTEGER REFERENCES users(id) ON DELETE SET NULL  -- 更新人
);
COMMENT ON TABLE registrations IS '挂号表:管理患者挂号与预约流程(可选择性地关联检查记录)';
COMMENT ON COLUMN registrations.id IS '挂号ID';
COMMENT ON COLUMN registrations.registration_number IS '挂号编号';
COMMENT ON COLUMN registrations.patient_id IS '患者ID';
COMMENT ON COLUMN registrations.examination_type_id IS '检查类型ID';
COMMENT ON COLUMN registrations.doctor_id IS '医生ID';
COMMENT ON COLUMN registrations.examination_id IS '检查记录ID(与examinations一对一关联，可选)';
COMMENT ON COLUMN registrations.department IS '科室';
COMMENT ON COLUMN registrations.registration_date IS '挂号日期';
COMMENT ON COLUMN registrations.registration_time IS '挂号时间';
COMMENT ON COLUMN registrations.scheduled_date IS '预约检查日期';
COMMENT ON COLUMN registrations.scheduled_time IS '预约检查时间';
COMMENT ON COLUMN registrations.priority IS '优先级:紧急/高/普通/低';
COMMENT ON COLUMN registrations.registration_type IS '挂号类型:急诊/预约/普通/复诊';
COMMENT ON COLUMN registrations.status IS '挂号状态:未签到/已签到/已取消';
COMMENT ON COLUMN registrations.registration_fee IS '挂号费';
COMMENT ON COLUMN registrations.payment_status IS '缴费状态:未缴费/已缴费/已退费';
COMMENT ON COLUMN registrations.payment_method IS '支付方式';
COMMENT ON COLUMN registrations.chief_complaint IS '主诉';
COMMENT ON COLUMN registrations.present_illness IS '现病史';
COMMENT ON COLUMN registrations.referral_doctor IS '转诊医生';
COMMENT ON COLUMN registrations.referral_hospital IS '转诊医院';
COMMENT ON COLUMN registrations.notes IS '备注';
COMMENT ON COLUMN registrations.check_in_time IS '签到时间';
COMMENT ON COLUMN registrations.queue_number IS '排队号码';
COMMENT ON COLUMN registrations.estimated_wait_time IS '预计等待时间(分钟)';
COMMENT ON COLUMN registrations.deleted_at IS '软删除时间戳(带时区)';
COMMENT ON COLUMN registrations.created_at IS '创建时间(带时区)';
COMMENT ON COLUMN registrations.updated_at IS '更新时间(带时区)';
COMMENT ON COLUMN registrations.created_by IS '创建人';
COMMENT ON COLUMN registrations.updated_by IS '更新人';

-- 一一对应约束:每个检查记录最多被一个挂号记录关联
ALTER TABLE registrations
    ADD CONSTRAINT uq_registrations_examination UNIQUE (examination_id);

-- 验证挂号与检查记录关联的一致性(可选触发器)
CREATE OR REPLACE FUNCTION validate_registration_examination_consistency()
RETURNS TRIGGER AS $$
BEGIN
    -- 如果设置了 examination_id，确保检查记录存在且未被其他挂号关联
    IF NEW.examination_id IS NOT NULL THEN
        -- 检查 examination 是否存在
        IF NOT EXISTS (
            SELECT 1 FROM examinations 
            WHERE id = NEW.examination_id 
            AND deleted_at IS NULL
        ) THEN
            RAISE EXCEPTION '检查记录不存在或已被删除: examination_id = %', NEW.examination_id;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
CREATE TRIGGER trg_registrations_validate_examination
BEFORE INSERT OR UPDATE ON registrations
FOR EACH ROW
EXECUTE FUNCTION validate_registration_examination_consistency();


-- 5. 眼底影像管理表
CREATE TABLE fundus_images (
    id SERIAL PRIMARY KEY,                                     -- 影像ID
    examination_id INTEGER NOT NULL REFERENCES examinations(id) ON DELETE CASCADE,  -- 检查记录ID
    image_number VARCHAR(50) NOT NULL,                         -- 影像编号
    eye_side VARCHAR(10) NOT NULL CHECK (eye_side IN ('OS', 'OD')),  -- 眼别 OD:右眼 OS:左眼
    capture_mode VARCHAR(20) NOT NULL CHECK (capture_mode IN ('gray', 'color')), -- 采集模式:灰度/彩色
    image_type VARCHAR(50),                                    -- 影像类型:彩色眼底照/荧光造影/OCT等
    image_position VARCHAR(50),                                -- 拍摄位置:后极部/周边部/黄斑区等
    file_path VARCHAR(500) NOT NULL,                           -- 文件路径
    file_name VARCHAR(255) NOT NULL,                           -- 文件名
    file_size BIGINT CHECK (file_size >= 0),                   -- 文件大小(字节)
    file_format VARCHAR(20),                                   -- 文件格式:JPEG/PNG/DICOM等
    image_quality VARCHAR(20) CHECK (image_quality IN ('excellent', 'good', 'fair', 'poor')),  -- 图像质量
    resolution VARCHAR(50),                                    -- 分辨率
    acquisition_device VARCHAR(100),                           -- 采集设备
    acquisition_parameters JSONB,                              -- 采集参数
    thumbnail_data TEXT,                                       -- 缩略图base64数据
    is_primary BOOLEAN DEFAULT false,                          -- 是否为主要图像
    upload_status VARCHAR(20) DEFAULT 'uploaded' CHECK (upload_status IN ('uploading', 'uploaded', 'failed', 'processing')),  -- 上传状态
    deleted_at TIMESTAMPTZ,                                   -- 软删除时间戳(带时区)
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,           -- 创建时间(带时区)
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,           -- 更新时间(带时区)
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL  -- 创建人
);
COMMENT ON TABLE fundus_images IS '眼底影像表:存储眼底检查产生的各种影像文件';
COMMENT ON COLUMN fundus_images.id IS '影像ID';
COMMENT ON COLUMN fundus_images.examination_id IS '检查记录ID';
COMMENT ON COLUMN fundus_images.image_number IS '影像编号';
COMMENT ON COLUMN fundus_images.eye_side IS '眼别 OD:右眼 OS:左眼';
COMMENT ON COLUMN fundus_images.capture_mode IS '采集模式:灰度/彩色';
COMMENT ON COLUMN fundus_images.image_type IS '影像类型:彩色眼底照/荧光造影/OCT等';
COMMENT ON COLUMN fundus_images.image_position IS '拍摄位置:后极部/周边部/黄斑区等';
COMMENT ON COLUMN fundus_images.file_path IS '文件路径';
COMMENT ON COLUMN fundus_images.file_name IS '文件名';
COMMENT ON COLUMN fundus_images.file_size IS '文件大小(字节)';
COMMENT ON COLUMN fundus_images.file_format IS '文件格式:JPEG/PNG/DICOM等';
COMMENT ON COLUMN fundus_images.image_quality IS '图像质量';
COMMENT ON COLUMN fundus_images.resolution IS '分辨率';
COMMENT ON COLUMN fundus_images.acquisition_device IS '采集设备';
COMMENT ON COLUMN fundus_images.acquisition_parameters IS '采集参数';
COMMENT ON COLUMN fundus_images.thumbnail_data IS '缩略图base64数据';
COMMENT ON COLUMN fundus_images.is_primary IS '是否为主要图像';
COMMENT ON COLUMN fundus_images.upload_status IS '上传状态';
COMMENT ON COLUMN fundus_images.deleted_at IS '软删除时间戳(带时区)';
COMMENT ON COLUMN fundus_images.created_at IS '创建时间(带时区)';
COMMENT ON COLUMN fundus_images.updated_at IS '更新时间(带时区)';
COMMENT ON COLUMN fundus_images.created_by IS '创建人';

-- 6. AI诊断信息管理表
CREATE TABLE ai_diagnoses (
    id SERIAL PRIMARY KEY,                                     -- AI诊断记录ID
    image_id INTEGER NOT NULL REFERENCES fundus_images(id) ON DELETE CASCADE,  -- 影像ID
    ai_model_name VARCHAR(100) NOT NULL,                       -- AI模型名称
    ai_model_version VARCHAR(50),                              -- AI模型版本
    diagnosis_result JSONB NOT NULL,                           -- 诊断结果(JSON格式)
    confidence_score DECIMAL(5,4) CHECK (confidence_score >= 0 AND confidence_score <= 1),  -- 置信度分数(0-1)
    processing_time_ms INTEGER,                                -- 处理时间(毫秒)
    severity_level VARCHAR(20) CHECK (severity_level IN ('normal', 'mild', 'moderate', 'severe', 'critical')),  -- 严重程度
    risk_assessment TEXT,                                     -- 风险评估
    recommended_actions TEXT,                                 -- 推荐措施
    diagnostic_markers JSONB,                                 -- 诊断标记点坐标
    processing_status VARCHAR(20) DEFAULT 'completed' CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed', 'timeout')),  -- 处理状态
    error_message TEXT,                                       -- 错误信息
    reviewed_by INTEGER REFERENCES users(id) ON DELETE SET NULL,  -- 审核医生ID
    review_status VARCHAR(20) DEFAULT 'pending' CHECK (review_status IN ('pending', 'approved', 'rejected', 'modified')),  -- 审核状态
    review_comments TEXT,                                     -- 审核意见
    reviewed_at TIMESTAMPTZ,                                  -- 审核时间(带时区)
    deleted_at TIMESTAMPTZ,                                   -- 软删除时间戳(带时区)
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,           -- 创建时间(带时区)
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP            -- 更新时间(带时区)
);
COMMENT ON TABLE ai_diagnoses IS 'AI诊断结果表:存储AI对眼底影像的诊断结果和相关信息';
COMMENT ON COLUMN ai_diagnoses.id IS 'AI诊断记录ID';
COMMENT ON COLUMN ai_diagnoses.image_id IS '影像ID';
COMMENT ON COLUMN ai_diagnoses.ai_model_name IS 'AI模型名称';
COMMENT ON COLUMN ai_diagnoses.ai_model_version IS 'AI模型版本';
COMMENT ON COLUMN ai_diagnoses.diagnosis_result IS '诊断结果(JSON格式)';
COMMENT ON COLUMN ai_diagnoses.confidence_score IS '置信度分数(0-1)';
COMMENT ON COLUMN ai_diagnoses.processing_time_ms IS '处理时间(毫秒)';
COMMENT ON COLUMN ai_diagnoses.severity_level IS '严重程度';
COMMENT ON COLUMN ai_diagnoses.risk_assessment IS '风险评估';
COMMENT ON COLUMN ai_diagnoses.recommended_actions IS '推荐措施';
COMMENT ON COLUMN ai_diagnoses.diagnostic_markers IS '诊断标记点坐标';
COMMENT ON COLUMN ai_diagnoses.processing_status IS '处理状态';
COMMENT ON COLUMN ai_diagnoses.error_message IS '错误信息';
COMMENT ON COLUMN ai_diagnoses.reviewed_by IS '审核医生ID';
COMMENT ON COLUMN ai_diagnoses.review_status IS '审核状态';
COMMENT ON COLUMN ai_diagnoses.review_comments IS '审核意见';
COMMENT ON COLUMN ai_diagnoses.reviewed_at IS '审核时间(带时区)';
COMMENT ON COLUMN ai_diagnoses.deleted_at IS '软删除时间戳(带时区)';
COMMENT ON COLUMN ai_diagnoses.created_at IS '创建时间(带时区)';
COMMENT ON COLUMN ai_diagnoses.updated_at IS '更新时间(带时区)';

-- 7. 诊断记录表(多次诊断支持)
CREATE TABLE diagnosis_records (
    id SERIAL PRIMARY KEY,                                     -- 诊断记录ID
    examination_id INTEGER NOT NULL REFERENCES examinations(id) ON DELETE CASCADE,  -- 检查记录ID
    doctor_id INTEGER NOT NULL REFERENCES users(id),          -- 诊断医生ID
    diagnosis_type VARCHAR(20) NOT NULL CHECK (diagnosis_type IN ('primary', 'secondary', 'differential', 'final')),  -- 诊断类型
    icd_code VARCHAR(20),                                     -- ICD-10疾病编码
    diagnosis_name VARCHAR(200) NOT NULL,                     -- 诊断名称
    diagnosis_description TEXT,                               -- 诊断描述
    severity VARCHAR(20) CHECK (severity IN ('mild', 'moderate', 'severe')),  -- 严重程度
    laterality VARCHAR(10) CHECK (laterality IN ('left', 'right', 'bilateral', 'unspecified')),  -- 患病侧别
    confidence_level VARCHAR(20) CHECK (confidence_level IN ('definite', 'probable', 'possible', 'rule_out')),  -- 诊断可信度
    supporting_evidence TEXT,                                 -- 支持证据
    differential_diagnoses TEXT[],                           -- 鉴别诊断
    treatment_plan TEXT,                                     -- 治疗方案
    prognosis TEXT,                                          -- 预后
    diagnosis_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,      -- 诊断时间(带时区)
    is_active BOOLEAN DEFAULT true,                          -- 是否有效
    deleted_at TIMESTAMPTZ,                                   -- 软删除时间戳(带时区)
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,          -- 创建时间(带时区)
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP           -- 更新时间(带时区)
);
COMMENT ON TABLE diagnosis_records IS '诊断记录表:支持一次检查的多次诊断和诊断历史追踪';
COMMENT ON COLUMN diagnosis_records.id IS '诊断记录ID';
COMMENT ON COLUMN diagnosis_records.examination_id IS '检查记录ID';
COMMENT ON COLUMN diagnosis_records.doctor_id IS '诊断医生ID';
COMMENT ON COLUMN diagnosis_records.diagnosis_type IS '诊断类型:初步/次要/鉴别/最终';
COMMENT ON COLUMN diagnosis_records.icd_code IS 'ICD-10疾病编码';
COMMENT ON COLUMN diagnosis_records.diagnosis_name IS '诊断名称';
COMMENT ON COLUMN diagnosis_records.diagnosis_description IS '诊断描述';
COMMENT ON COLUMN diagnosis_records.severity IS '严重程度';
COMMENT ON COLUMN diagnosis_records.laterality IS '患病侧别';
COMMENT ON COLUMN diagnosis_records.confidence_level IS '诊断可信度';
COMMENT ON COLUMN diagnosis_records.supporting_evidence IS '支持证据';
COMMENT ON COLUMN diagnosis_records.differential_diagnoses IS '鉴别诊断';
COMMENT ON COLUMN diagnosis_records.treatment_plan IS '治疗方案';
COMMENT ON COLUMN diagnosis_records.prognosis IS '预后';
COMMENT ON COLUMN diagnosis_records.diagnosis_date IS '诊断时间(带时区)';
COMMENT ON COLUMN diagnosis_records.is_active IS '是否有效';
COMMENT ON COLUMN diagnosis_records.deleted_at IS '软删除时间戳(带时区)';
COMMENT ON COLUMN diagnosis_records.created_at IS '创建时间(带时区)';
COMMENT ON COLUMN diagnosis_records.updated_at IS '更新时间(带时区)';

-- 8. 随访管理表
CREATE TABLE follow_ups (
    id SERIAL PRIMARY KEY,                                     -- 随访ID
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,  -- 患者ID
    original_examination_id INTEGER REFERENCES examinations(id) ON DELETE SET NULL,  -- 原始检查ID
    follow_up_type VARCHAR(50) NOT NULL,                      -- 随访类型
    scheduled_date DATE NOT NULL,                             -- 预约随访日期
    actual_date DATE,                                         -- 实际随访日期
    follow_up_interval_days INTEGER,                          -- 随访间隔天数
    priority VARCHAR(20) CHECK (priority IN ('low', 'medium', 'high', 'urgent')),  -- 优先级
    status VARCHAR(20) NOT NULL DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'completed', 'missed', 'cancelled', 'rescheduled')),  -- 随访状态
    reminder_sent BOOLEAN DEFAULT false,                      -- 是否已发送提醒
    reminder_date DATE,                                       -- 提醒日期
    follow_up_notes TEXT,                                     -- 随访说明
    outcome TEXT,                                            -- 随访结果
    next_follow_up_date DATE,                                 -- 下次随访日期
    assigned_doctor_id INTEGER REFERENCES users(id) ON DELETE SET NULL,  -- 负责医生ID
    deleted_at TIMESTAMPTZ,                                   -- 软删除时间戳(带时区)
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,           -- 创建时间(带时区)
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,           -- 更新时间(带时区)
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL -- 创建人
);
COMMENT ON TABLE follow_ups IS '随访管理表:管理患者的随访计划和执行情况';
COMMENT ON COLUMN follow_ups.id IS '随访ID';
COMMENT ON COLUMN follow_ups.patient_id IS '患者ID';
COMMENT ON COLUMN follow_ups.original_examination_id IS '原始检查ID';
COMMENT ON COLUMN follow_ups.follow_up_type IS '随访类型:定期复查/病情变化/治疗评估等';
COMMENT ON COLUMN follow_ups.scheduled_date IS '预约随访日期';
COMMENT ON COLUMN follow_ups.actual_date IS '实际随访日期';
COMMENT ON COLUMN follow_ups.follow_up_interval_days IS '随访间隔天数';
COMMENT ON COLUMN follow_ups.priority IS '优先级';
COMMENT ON COLUMN follow_ups.status IS '随访状态';
COMMENT ON COLUMN follow_ups.reminder_sent IS '是否已发送提醒';
COMMENT ON COLUMN follow_ups.reminder_date IS '提醒日期';
COMMENT ON COLUMN follow_ups.follow_up_notes IS '随访说明';
COMMENT ON COLUMN follow_ups.outcome IS '随访结果';
COMMENT ON COLUMN follow_ups.next_follow_up_date IS '下次随访日期';
COMMENT ON COLUMN follow_ups.assigned_doctor_id IS '负责医生ID';
COMMENT ON COLUMN follow_ups.deleted_at IS '软删除时间戳(带时区)';
COMMENT ON COLUMN follow_ups.created_at IS '创建时间(带时区)';
COMMENT ON COLUMN follow_ups.updated_at IS '更新时间(带时区)';
COMMENT ON COLUMN follow_ups.created_by IS '创建人';

-- 9. 角色表
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,                                     -- 角色ID
    role_name VARCHAR(50) NOT NULL UNIQUE,                    -- 角色名称
    role_code VARCHAR(20) NOT NULL UNIQUE,                    -- 角色代码
    description TEXT,                                         -- 角色描述
    is_system_role BOOLEAN DEFAULT false,                     -- 是否为系统内置角色
    is_active BOOLEAN DEFAULT true,                           -- 是否启用
    deleted_at TIMESTAMPTZ,                                   -- 软删除时间戳(带时区)
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,           -- 创建时间(带时区)
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP            -- 更新时间(带时区)
);
COMMENT ON TABLE roles IS '角色表:定义系统中的各种角色';
COMMENT ON COLUMN roles.id IS '角色ID';
COMMENT ON COLUMN roles.role_name IS '角色名称';
COMMENT ON COLUMN roles.role_code IS '角色代码';
COMMENT ON COLUMN roles.description IS '角色描述';
COMMENT ON COLUMN roles.is_system_role IS '是否为系统内置角色';
COMMENT ON COLUMN roles.is_active IS '是否启用';
COMMENT ON COLUMN roles.deleted_at IS '软删除时间戳(带时区)';
COMMENT ON COLUMN roles.created_at IS '创建时间(带时区)';
COMMENT ON COLUMN roles.updated_at IS '更新时间(带时区)';

-- 10. 权限表
CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,                                     -- 权限ID
    permission_name VARCHAR(100) NOT NULL UNIQUE,             -- 权限名称
    permission_code VARCHAR(50) NOT NULL UNIQUE,              -- 权限代码
    resource VARCHAR(50) NOT NULL,                            -- 资源名称
    action VARCHAR(50) NOT NULL,                              -- 操作类型:create/read/update/delete
    description TEXT,                                         -- 权限描述
    is_active BOOLEAN DEFAULT true,                           -- 是否启用
    deleted_at TIMESTAMPTZ,                                   -- 软删除时间戳(带时区)
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP            -- 创建时间(带时区)
);
COMMENT ON TABLE permissions IS '权限表:定义系统中的各种权限';
COMMENT ON COLUMN permissions.id IS '权限ID';
COMMENT ON COLUMN permissions.permission_name IS '权限名称';
COMMENT ON COLUMN permissions.permission_code IS '权限代码';
COMMENT ON COLUMN permissions.resource IS '资源名称';
COMMENT ON COLUMN permissions.action IS '操作类型:create/read/update/delete';
COMMENT ON COLUMN permissions.description IS '权限描述';
COMMENT ON COLUMN permissions.is_active IS '是否启用';
COMMENT ON COLUMN permissions.deleted_at IS '软删除时间戳(带时区)';
COMMENT ON COLUMN permissions.created_at IS '创建时间(带时区)';

-- 11. 用户角色关联表
CREATE TABLE user_roles (
    id SERIAL PRIMARY KEY,                                     -- 关联ID
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,   -- 用户ID
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,   -- 角色ID
    assigned_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,           -- 分配时间(带时区)
    assigned_by INTEGER REFERENCES users(id) ON DELETE SET NULL,   -- 分配人
    is_active BOOLEAN DEFAULT true,                            -- 是否有效
    deleted_at TIMESTAMPTZ,                                      -- 软删除时间戳(带时区)
    UNIQUE(user_id, role_id)                                  -- 用户-角色唯一约束
);
COMMENT ON TABLE user_roles IS '用户角色关联表:管理用户与角色的关系';
COMMENT ON COLUMN user_roles.id IS '关联ID';
COMMENT ON COLUMN user_roles.user_id IS '用户ID';
COMMENT ON COLUMN user_roles.role_id IS '角色ID';
COMMENT ON COLUMN user_roles.assigned_at IS '分配时间(带时区)';
COMMENT ON COLUMN user_roles.assigned_by IS '分配人';
COMMENT ON COLUMN user_roles.is_active IS '是否有效';
COMMENT ON COLUMN user_roles.deleted_at IS '软删除时间戳(带时区)';

-- 12. 角色权限关联表
CREATE TABLE role_permissions (
    id SERIAL PRIMARY KEY,                                     -- 关联ID
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,    -- 角色ID
    permission_id INTEGER NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,  -- 权限ID
    granted_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,            -- 授权时间(带时区)
    granted_by INTEGER REFERENCES users(id) ON DELETE SET NULL,-- 授权人
    is_active BOOLEAN DEFAULT true,                            -- 是否有效
    deleted_at TIMESTAMPTZ,                                      -- 软删除时间戳(带时区)
    UNIQUE(role_id, permission_id)                           -- 角色-权限唯一约束
);
COMMENT ON TABLE role_permissions IS '角色权限关联表:管理角色与权限的关系';
COMMENT ON COLUMN role_permissions.id IS '关联ID';
COMMENT ON COLUMN role_permissions.role_id IS '角色ID';
COMMENT ON COLUMN role_permissions.permission_id IS '权限ID';
COMMENT ON COLUMN role_permissions.granted_at IS '授权时间(带时区)';
COMMENT ON COLUMN role_permissions.granted_by IS '授权人';
COMMENT ON COLUMN role_permissions.is_active IS '是否有效';
COMMENT ON COLUMN role_permissions.deleted_at IS '软删除时间戳(带时区)';

-- 13. 系统日志管理表
CREATE TABLE system_logs (
    id SERIAL PRIMARY KEY,                                     -- 日志ID
    log_level VARCHAR(20) NOT NULL CHECK (log_level IN ('DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL')),  -- 日志级别
    module VARCHAR(50),                                       -- 模块名称
    action VARCHAR(100),                                      -- 操作名称
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,  -- 操作用户ID
    ip_address INET,                                         -- IP地址
    user_agent TEXT,                                         -- 用户代理
    request_id VARCHAR(100),                                 -- 请求ID
    session_id VARCHAR(100),                                 -- 会话ID
    resource_type VARCHAR(50),                               -- 资源类型
    resource_id VARCHAR(100),                                -- 资源ID
    operation_result VARCHAR(20) CHECK (operation_result IN ('success', 'failure', 'partial')),  -- 操作结果
    message TEXT NOT NULL,                                   -- 日志消息
    error_code VARCHAR(50),                                  -- 错误代码
    error_details TEXT,                                      -- 错误详情
    execution_time_ms INTEGER,                               -- 执行耗时(毫秒)
    additional_data JSONB,                                   -- 额外数据(JSON)
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP           -- 创建时间(带时区)
);
COMMENT ON TABLE system_logs IS '系统日志表:记录系统操作和错误信息';
COMMENT ON COLUMN system_logs.id IS '日志ID';
COMMENT ON COLUMN system_logs.log_level IS '日志级别';
COMMENT ON COLUMN system_logs.module IS '模块名称';
COMMENT ON COLUMN system_logs.action IS '操作名称';
COMMENT ON COLUMN system_logs.user_id IS '操作用户ID';
COMMENT ON COLUMN system_logs.ip_address IS 'IP地址';
COMMENT ON COLUMN system_logs.user_agent IS '用户代理';
COMMENT ON COLUMN system_logs.request_id IS '请求ID';
COMMENT ON COLUMN system_logs.session_id IS '会话ID';
COMMENT ON COLUMN system_logs.resource_type IS '资源类型';
COMMENT ON COLUMN system_logs.resource_id IS '资源ID';
COMMENT ON COLUMN system_logs.operation_result IS '操作结果';
COMMENT ON COLUMN system_logs.message IS '日志消息';
COMMENT ON COLUMN system_logs.error_code IS '错误代码';
COMMENT ON COLUMN system_logs.error_details IS '错误详情';
COMMENT ON COLUMN system_logs.execution_time_ms IS '执行耗时(毫秒)';
COMMENT ON COLUMN system_logs.additional_data IS '额外数据';
COMMENT ON COLUMN system_logs.created_at IS '创建时间(带时区)';

-- 创建触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 为每个有updated_at的表创建触发器
CREATE TRIGGER trigger_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trigger_patients_updated_at BEFORE UPDATE ON patients FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trigger_examination_types_updated_at BEFORE UPDATE ON examination_types FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trigger_examinations_updated_at BEFORE UPDATE ON examinations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trigger_fundus_images_updated_at BEFORE UPDATE ON fundus_images FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trigger_ai_diagnoses_updated_at BEFORE UPDATE ON ai_diagnoses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trigger_diagnosis_records_updated_at BEFORE UPDATE ON diagnosis_records FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trigger_follow_ups_updated_at BEFORE UPDATE ON follow_ups FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trigger_roles_updated_at BEFORE UPDATE ON roles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trigger_registrations_updated_at BEFORE UPDATE ON registrations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 索引优化
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_department ON users(department);
CREATE INDEX idx_users_deleted_at ON users(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_patients_name ON patients(name);
CREATE INDEX idx_patients_status ON patients(status);
CREATE INDEX idx_patients_deleted_at ON patients(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_examinations_patient_id ON examinations(patient_id);
CREATE INDEX idx_examinations_doctor_id ON examinations(doctor_id);
CREATE INDEX idx_examinations_date_status ON examinations(examination_date, status);
CREATE INDEX idx_examinations_status ON examinations(status);
CREATE INDEX idx_examinations_deleted_at ON examinations(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_registrations_patient_id ON registrations(patient_id);
CREATE INDEX idx_registrations_doctor_id ON registrations(doctor_id);
CREATE INDEX idx_registrations_examination_id ON registrations(examination_id);
CREATE INDEX idx_registrations_status ON registrations(status);
CREATE INDEX idx_registrations_scheduled_date ON registrations(scheduled_date);
CREATE INDEX idx_registrations_registration_date ON registrations(registration_date);
CREATE INDEX idx_registrations_queue_number ON registrations(queue_number);
-- 队列号常见按科室+日期分区排序，这里增加组合索引
CREATE INDEX idx_registrations_department_date_queue ON registrations(department, registration_date, queue_number);
CREATE INDEX idx_registrations_deleted_at ON registrations(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_fundus_images_examination_id ON fundus_images(examination_id);
-- 防止同一检查的影像编号重复
CREATE UNIQUE INDEX unique_fundus_image_per_exam_number ON fundus_images(examination_id, image_number);
CREATE INDEX idx_fundus_images_deleted_at ON fundus_images(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_ai_diagnoses_image_id ON ai_diagnoses(image_id);
CREATE INDEX idx_ai_diagnoses_reviewed_by ON ai_diagnoses(reviewed_by);
CREATE INDEX idx_ai_diagnoses_review_status ON ai_diagnoses(review_status);
CREATE INDEX idx_ai_diagnoses_deleted_at ON ai_diagnoses(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_diagnosis_records_examination_id ON diagnosis_records(examination_id);
CREATE INDEX idx_diagnosis_records_doctor_id ON diagnosis_records(doctor_id);
CREATE INDEX idx_diagnosis_records_deleted_at ON diagnosis_records(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_follow_ups_patient_id ON follow_ups(patient_id);
CREATE INDEX idx_follow_ups_assigned_doctor_id ON follow_ups(assigned_doctor_id);
CREATE INDEX idx_follow_ups_status_scheduled_date ON follow_ups(status, scheduled_date);
CREATE INDEX idx_follow_ups_reminder_sent ON follow_ups(reminder_sent) WHERE reminder_sent = false;
CREATE INDEX idx_follow_ups_deleted_at ON follow_ups(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX idx_user_roles_role_id ON user_roles(role_id);
CREATE INDEX idx_user_roles_deleted_at ON user_roles(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_role_permissions_role_id ON role_permissions(role_id);
CREATE INDEX idx_role_permissions_permission_id ON role_permissions(permission_id);
CREATE INDEX idx_role_permissions_deleted_at ON role_permissions(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_system_logs_user_id ON system_logs(user_id);
CREATE INDEX idx_system_logs_created_at ON system_logs(created_at);

-- 条件唯一索引:只对医生用户要求执业证书号唯一
CREATE UNIQUE INDEX unique_doctor_license 
ON users(license_number) 
WHERE user_type = 'doctor' AND license_number IS NOT NULL AND deleted_at IS NULL;

COMMIT;