# 前后端安全对接检查报告

## 检查日期
2025年11月1日

## 检查结果

### ❌ 发现的问题

#### 1. **密码加密盐值不匹配** 🔴 严重

**前端** (`frontend/src/utils/crypto.js` 第 59-63 行):
```javascript
export function hashPassword(password) {
  const saltedPassword = password + 'eyes_remk_salt_2024';
  return sha256Hash(saltedPassword);
}
```

**后端** (`utils/jwt_auth.py` 第 14 行):
```python
PASSWORD_SALT = "eyes_remk_system_salt_change_in_production"
```

**问题**: 前后端使用的盐值不同！
- 前端：`'eyes_remk_salt_2024'`
- 后端：`"eyes_remk_system_salt_change_in_production"`

**影响**: 登录将永远失败，因为前后端计算的密码哈希值不一致。

**优先级**: 🔴 **极高** - 必须立即修复

---

#### 2. **JWT 响应字段映射问题** 🟡 中等

**后端响应** (`interface/auth.py` 第 151-169 行):
```python
response_data = {
    "token": token_data["access_token"],        # 注意：access_token → token
    "refresh_token": token_data["refresh_token"],
    "token_type": token_data["token_type"],
    "expires_at": token_data["expires_at"],
    "expires_in": token_data["expires_in"],
    "user": { ... },
    "permissions": permissions
}
```

**前端处理** (`frontend/src/views/Login.vue` 第 134-143 行):
```javascript
const loginData = response.data || response;

await userStore.setUserInfo({
  token: loginData.token || response.token,          // ✅ 正确
  refreshToken: loginData.refresh_token || response.refresh_token,  // ✅ 正确
  user: loginData.user || response.user,             // ✅ 正确
  permissions: loginData.permissions || response.permissions,  // ✅ 正确
  expiresAt: loginData.expires_at || response.expires_at  // ✅ 正确
});
```

**状态**: ✅ 这部分映射正确

---

## 修复方案

### 方案 1：统一盐值（推荐） ⭐

**选择**: 使用后端的盐值（更长、更安全）

#### 步骤 1：修改前端密码加密函数

**文件**: `frontend/src/utils/crypto.js`

```javascript
// 修改前
export function hashPassword(password) {
  const saltedPassword = password + 'eyes_remk_salt_2024';
  return sha256Hash(saltedPassword);
}

// 修改后
export function hashPassword(password) {
  // 使用与后端相同的盐值
  const saltedPassword = password + 'eyes_remk_system_salt_change_in_production';
  return sha256Hash(saltedPassword);
}
```

#### 步骤 2：更新配置文件

建议创建共享配置：

**新建文件**: `frontend/src/config/security.js`

```javascript
/**
 * 安全配置
 * 注意：这些值应该与后端保持一致
 */

// 密码加密盐值（应与后端 utils/jwt_auth.py 中的 PASSWORD_SALT 保持一致）
export const PASSWORD_SALT = 'eyes_remk_system_salt_change_in_production';

// JWT 密钥（仅用于前端验证，不用于签名）
export const JWT_SECRET = 'your-secret-key-change-this-in-production-to-a-secure-random-string';

// 其他安全配置
export const SECURITY_CONFIG = {
  // 密码最小长度
  PASSWORD_MIN_LENGTH: 8,
  
  // 密码最大长度
  PASSWORD_MAX_LENGTH: 20,
  
  // 用户名最小长度
  USERNAME_MIN_LENGTH: 5,
  
  // 用户名最大长度
  USERNAME_MAX_LENGTH: 50,
  
  // Token 过期时间（分钟）
  TOKEN_EXPIRE_MINUTES: 60 * 24, // 24小时
  
  // 刷新令牌过期时间（天）
  REFRESH_TOKEN_EXPIRE_DAYS: 7,
};

export default {
  PASSWORD_SALT,
  JWT_SECRET,
  ...SECURITY_CONFIG
};
```

**修改**: `frontend/src/utils/crypto.js`

```javascript
import CryptoJS from 'crypto-js';
import { PASSWORD_SALT } from '@/config/security';

/**
 * 密码加密（用于登录）
 * @param {string} password 原始密码
 * @returns {string} 哈希后的密码
 */
export function hashPassword(password) {
  // 使用与后端相同的盐值
  const saltedPassword = password + PASSWORD_SALT;
  return sha256Hash(saltedPassword);
}
```

---

### 方案 2：后端适配前端（不推荐）

如果已有大量用户数据，需要后端兼容旧盐值：

```python
# utils/jwt_auth.py

# 旧盐值（兼容前端旧版本）
OLD_PASSWORD_SALT = "eyes_remk_salt_2024"
# 新盐值
PASSWORD_SALT = "eyes_remk_system_salt_change_in_production"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码（兼容新旧盐值）"""
    try:
        # 尝试新盐值
        new_hash = hash_password(plain_password)
        if new_hash == hashed_password:
            return True
        
        # 尝试旧盐值
        old_hash = hash_password_old(plain_password)
        return old_hash == hashed_password
    except Exception as e:
        log.error(f"密码验证失败: {str(e)}")
        return False
```

**不推荐原因**: 增加了系统复杂度，降低了安全性。

---

## 验证步骤

### 1. 修复前的测试

```bash
# 测试当前状态（应该失败）
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "错误的哈希值"
  }'
```

### 2. 修复后的测试

#### 步骤 A：计算正确的密码哈希

**使用 Python 测试**:
```python
import hashlib

# 原始密码
password = "admin123"

# 前端第一次SHA-256（模拟前端加密）
frontend_salt = "eyes_remk_salt_2024"  # 修复前
frontend_hash = hashlib.sha256((password + frontend_salt).encode()).hexdigest()
print(f"前端哈希: {frontend_hash}")

# 后端再次SHA-256
backend_salt = "eyes_remk_system_salt_change_in_production"
backend_hash = hashlib.sha256((frontend_hash + backend_salt).encode()).hexdigest()
print(f"后端存储: {backend_hash}")
```

#### 步骤 B：使用浏览器控制台测试

```javascript
// 在浏览器控制台执行
import { hashPassword } from '@/utils/crypto';

const password = "admin123";
const hashed = hashPassword(password);
console.log('前端加密结果:', hashed);

// 然后发送登录请求
authAPI.login('admin', hashed).then(response => {
  console.log('登录响应:', response);
});
```

### 3. 完整集成测试

```bash
# 启动后端
cd /Users/stunum/workspace/eyes/remk_python
source .venv/bin/activate
uvicorn main:app --reload --port 8080

# 启动前端
cd frontend
npm run dev

# 在浏览器访问 http://localhost:5173
# 尝试登录
```

---

## 安全建议

### 1. 生产环境配置 🔒

#### 后端配置
**文件**: `utils/jwt_auth.py`

```python
import os

# 从环境变量读取（生产环境必须配置）
PASSWORD_SALT = os.getenv(
    'PASSWORD_SALT',
    'eyes_remk_system_salt_change_in_production'  # 开发环境默认值
)

SECRET_KEY = os.getenv(
    'JWT_SECRET_KEY',
    'your-secret-key-change-this-in-production-to-a-secure-random-string'
)

# 警告：生产环境未配置
if 'production' in os.getenv('ENVIRONMENT', '').lower():
    if PASSWORD_SALT == 'eyes_remk_system_salt_change_in_production':
        print("⚠️  警告: 生产环境使用默认密码盐值，请设置 PASSWORD_SALT 环境变量")
    if SECRET_KEY == 'your-secret-key-change-this-in-production-to-a-secure-random-string':
        print("⚠️  警告: 生产环境使用默认JWT密钥，请设置 JWT_SECRET_KEY 环境变量")
```

#### 前端配置
**文件**: `frontend/src/config/security.js`

```javascript
// 从环境变量读取（构建时注入）
export const PASSWORD_SALT = import.meta.env.VITE_PASSWORD_SALT || 
  'eyes_remk_system_salt_change_in_production';

// 检查是否为生产环境
if (import.meta.env.PROD && PASSWORD_SALT === 'eyes_remk_system_salt_change_in_production') {
  console.warn('⚠️  警告: 生产环境使用默认密码盐值');
}
```

**文件**: `frontend/.env.production`

```bash
# 生产环境配置
VITE_PASSWORD_SALT=your_production_password_salt_here
VITE_API_BASE_URL=https://your-domain.com/api
```

### 2. 密码加密最佳实践 ✅

当前实现：
```
用户输入密码 → 前端SHA256+盐值 → 后端SHA256+盐值 → 数据库
```

**优点**:
- ✅ 双重哈希
- ✅ 前端加密（防止明文传输）
- ✅ 后端加密（防止前端绕过）

**建议改进**:
1. 使用 HTTPS 确保传输安全
2. 考虑使用更强的哈希算法（bcrypt, Argon2）
3. 实施密码复杂度策略
4. 添加登录失败次数限制

### 3. JWT 最佳实践 🔐

#### 已实现 ✅
- [x] 访问令牌（短期有效）
- [x] 刷新令牌（长期有效）
- [x] Token 类型验证
- [x] 自动刷新机制

#### 建议改进 📝
- [ ] 实现 Token 黑名单（Redis）
- [ ] 添加设备指纹验证
- [ ] 记录登录历史
- [ ] 异常登录检测

---

## 检查清单

### 立即修复 ❗
- [ ] 统一前后端密码盐值
- [ ] 测试登录功能
- [ ] 更新初始化数据中的密码哈希

### 优化改进 📋
- [ ] 创建共享安全配置文件
- [ ] 添加环境变量支持
- [ ] 实施生产环境检查
- [ ] 添加密码强度验证

### 安全加固 🔒
- [ ] 启用 HTTPS
- [ ] 实施 CORS 白名单
- [ ] 添加请求频率限制
- [ ] 实施 SQL 注入防护
- [ ] 添加 XSS 防护

---

## 附录

### A. 密码哈希计算示例

#### Python 后端计算
```python
import hashlib

def compute_password_hash(plain_password, salt):
    """计算密码哈希"""
    salted = f"{plain_password}{salt}"
    return hashlib.sha256(salted.encode('utf-8')).hexdigest()

# 示例
password = "admin123"
salt = "eyes_remk_system_salt_change_in_production"
hash_value = compute_password_hash(password, salt)
print(f"密码哈希: {hash_value}")
```

#### JavaScript 前端计算
```javascript
import CryptoJS from 'crypto-js';

function computePasswordHash(plainPassword, salt) {
  const salted = plainPassword + salt;
  return CryptoJS.SHA256(salted).toString();
}

// 示例
const password = "admin123";
const salt = "eyes_remk_system_salt_change_in_production";
const hashValue = computePasswordHash(password, salt);
console.log('密码哈希:', hashValue);
```

### B. 初始密码重置

如果需要重置管理员密码：

```sql
-- 计算新密码哈希（Python）
-- password = 'admin123'
-- hashed = hashlib.sha256((password + 'eyes_remk_system_salt_change_in_production').encode()).hexdigest()

UPDATE users 
SET password_hash = '计算出的哈希值'
WHERE username = 'admin';
```

---

## 总结

**关键问题**: 前后端密码盐值不匹配导致登录功能完全失效。

**修复优先级**: 🔴 极高

**修复时间**: 约 15 分钟

**建议**: 立即执行方案 1（统一盐值），并进行完整测试。

**后续**: 实施安全最佳实践，定期安全审计。

