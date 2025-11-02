/**
 * 安全配置
 * 注意：这些值必须与后端保持一致
 */

// 密码加密盐值（必须与后端 utils/jwt_auth.py 中的 PASSWORD_SALT 保持一致）
// 生产环境应从环境变量读取
export const PASSWORD_SALT = import.meta.env.VITE_PASSWORD_SALT || 
  'eyes_remk_system_salt_change_in_production';

// JWT 密钥（仅用于前端验证，不用于签名）
export const JWT_SECRET = import.meta.env.VITE_JWT_SECRET ||
  'your-secret-key-change-this-in-production-to-a-secure-random-string';

// 密码验证规则
export const PASSWORD_RULES = {
  // 最小长度
  MIN_LENGTH: 8,
  // 最大长度
  MAX_LENGTH: 20,
  // 是否需要大写字母
  REQUIRE_UPPERCASE: false,
  // 是否需要小写字母
  REQUIRE_LOWERCASE: true,
  // 是否需要数字
  REQUIRE_NUMBER: true,
  // 是否需要特殊字符
  REQUIRE_SPECIAL: false,
};

// 用户名验证规则
export const USERNAME_RULES = {
  // 最小长度
  MIN_LENGTH: 5,
  // 最大长度
  MAX_LENGTH: 50,
  // 允许的字符（正则表达式）
  PATTERN: /^[a-zA-Z0-9_]+$/,
  // 错误提示
  PATTERN_MESSAGE: '用户名只能包含字母、数字和下划线',
};

// Token 配置
export const TOKEN_CONFIG = {
  // 访问令牌过期时间（分钟）
  ACCESS_TOKEN_EXPIRE_MINUTES: 60 * 24, // 24小时
  // 刷新令牌过期时间（天）
  REFRESH_TOKEN_EXPIRE_DAYS: 7,
  // 令牌即将过期时间阈值（分钟）
  TOKEN_REFRESH_THRESHOLD: 30,
};

// 安全检查（开发环境警告）
if (import.meta.env.DEV) {
  console.log('🔐 安全配置已加载（开发模式）');
  console.log(`- 密码盐值: ${PASSWORD_SALT.substring(0, 20)}...`);
}

// 生产环境安全检查
if (import.meta.env.PROD) {
  // 检查是否使用默认配置
  const defaultSalt = 'eyes_remk_system_salt_change_in_production';
  const defaultSecret = 'your-secret-key-change-this-in-production-to-a-secure-random-string';
  
  if (PASSWORD_SALT === defaultSalt) {
    console.warn('⚠️  警告: 生产环境使用默认密码盐值，请设置 VITE_PASSWORD_SALT 环境变量');
  }
  
  if (JWT_SECRET === defaultSecret) {
    console.warn('⚠️  警告: 生产环境使用默认JWT密钥，请设置 VITE_JWT_SECRET 环境变量');
  }
}

// 导出所有配置
export default {
  PASSWORD_SALT,
  JWT_SECRET,
  PASSWORD_RULES,
  USERNAME_RULES,
  TOKEN_CONFIG,
};

