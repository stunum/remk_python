# 患者管理API快速参考

## 📋 API端点速查

```
基础路径: /api/patients
```

| 操作 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 列表 | GET | `/api/patients` | 分页查询患者列表 |
| 详情 | GET | `/api/patients/{id}` | 获取单个患者信息 |
| 查询 | GET | `/api/patients/by-patient-id/{patient_id}` | 按患者编号查询 |
| 创建 | POST | `/api/patients` | 创建新患者 |
| 更新 | PUT | `/api/patients/{id}` | 更新患者信息 |
| 删除 | DELETE | `/api/patients` | 批量软删除 |

## 🔍 查询参数

### 列表查询 (GET /api/patients)

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `page` | int | 是 | 页码（从1开始） |
| `page_size` | int | 是 | 每页数量（1-100） |
| `name` | string | 否 | 姓名模糊查询 |
| `patient_id` | string | 否 | 患者编号模糊查询 |
| `status` | string | 否 | `active`/`inactive`/`deceased` |
| `gender` | string | 否 | `male`/`female`/`other` |

## 📦 响应格式

### 标准响应结构
```json
{
  "code": 200,
  "msg": "success",
  "data": { /* 业务数据 */ }
}
```

### 列表响应
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "patients": [...],
    "pagination": {
      "page": 1,
      "page_size": 10,
      "total": 100,
      "total_pages": 10
    }
  }
}
```

### 单条记录响应
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "id": 1,
    "patient_id": "P001",
    "name": "张三",
    "gender": "male",
    "birth_date": "1990-01-01",
    "phone": "13800138000",
    "email": "zhangsan@example.com",
    "status": "active",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

## ✏️ 创建/更新字段

### 必填字段（创建）
- ✅ `patient_id` - 患者编号（唯一）
- ✅ `name` - 患者姓名

### 可选字段
- `gender` - 性别: `male`/`female`/`other`
- `birth_date` - 出生日期: `YYYY-MM-DD`
- `phone` - 联系电话
- `email` - 邮箱
- `address` - 地址
- `emergency_contact` - 紧急联系人
- `emergency_phone` - 紧急联系人电话
- `medical_history` - 病史
- `allergies` - 过敏史
- `current_medications` - 当前用药
- `insurance_info` - 医保信息（JSON）
- `status` - 状态: `active`/`inactive`/`deceased`（默认`active`）

### 不可更新字段
- ❌ `patient_id` - 患者编号（创建后不可更改）
- ❌ `id` - 内部ID（自动生成）
- ❌ `created_at` - 创建时间（自动生成）
- ❌ `updated_at` - 更新时间（自动更新）

## 💻 前端调用示例

### 导入API
```javascript
import patientAPI from '@/api/patient';
```

### 获取列表
```javascript
// 基础查询
const response = await patientAPI.getPatients({
  page: 1,
  pageSize: 10
});

// 带搜索
const response = await patientAPI.getPatients({
  page: 1,
  pageSize: 10,
  name: '张',
  status: 'active'
});

// 解析响应
if (response.code === 200) {
  const patients = response.data.patients;
  const pagination = response.data.pagination;
}
```

### 获取详情
```javascript
const response = await patientAPI.getPatient(patientId);
if (response.code === 200) {
  const patient = response.data;
}
```

### 创建患者
```javascript
const newPatient = {
  patient_id: 'P999',
  name: '测试患者',
  gender: 'male',
  birth_date: '1990-01-01',
  phone: '13800138000',
  status: 'active'
};

const response = await patientAPI.createPatient(newPatient);
if (response.code === 200) {
  console.log('创建成功', response.data);
}
```

### 更新患者
```javascript
const updateData = {
  name: '新姓名',
  phone: '13900139000',
  status: 'inactive'
};

const response = await patientAPI.updatePatient(patientId, updateData);
if (response.code === 200) {
  console.log('更新成功', response.data);
}
```

### 删除患者
```javascript
// 删除单个
await patientAPI.deletePatient(patientId);

// 批量删除
await patientAPI.deletePatients([1, 2, 3], currentUserId);
```

## 🎯 数据处理工具函数

### 日期格式化
```javascript
// API提交格式（YYYY-MM-DD）
const formatDateForAPI = (date) => {
  if (!date) return null;
  if (typeof date === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(date)) {
    return date;
  }
  const d = new Date(date);
  return isNaN(d.getTime()) ? null : d.toISOString().split('T')[0];
};

// 日期选择器格式
const formatDateForPicker = (date) => {
  if (!date) return null;
  const d = new Date(date);
  return isNaN(d.getTime()) ? null : d.toISOString().split('T')[0];
};

// 界面显示格式
const formatDate = (date) => {
  if (!date) return '-';
  const d = new Date(date);
  return isNaN(d.getTime()) ? '-' : d.toLocaleDateString('zh-CN');
};
```

### 响应处理
```javascript
// 判断响应是否成功
const isResponseSuccess = (response) => {
  return response && response.code === 200;
};

// 获取响应消息
const getResponseMessage = (response) => {
  return response?.msg || '操作失败';
};
```

## ⚠️ 常见错误

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 400 | 参数错误/患者编号已存在 | 检查请求参数和唯一性 |
| 404 | 患者未找到 | 确认患者ID正确且未被删除 |
| 422 | 验证错误 | 检查字段格式和必填项 |
| 500 | 服务器错误 | 查看后端日志 |

## 📝 注意事项

1. **软删除**: 删除操作不会真正删除数据，只标记 `deleted_at` 字段
2. **日期格式**: 必须使用 `YYYY-MM-DD` 格式
3. **性别值**: 只能是 `male`、`female` 或 `other`
4. **状态值**: 只能是 `active`、`inactive` 或 `deceased`
5. **患者编号**: 创建后不可修改，必须唯一
6. **分页**: 页码从 1 开始，不是 0
7. **响应解析**: 数据在 `response.data`，列表在 `response.data.patients`

## 🔗 相关文档

- [详细适配文档](../PATIENT_API_ADAPTATION.md)
- [集成总结](../PATIENT_API_INTEGRATION_SUMMARY.md)
- 前端代码: `src/components/PatientManagement.vue`
- API封装: `src/api/patient.js`

