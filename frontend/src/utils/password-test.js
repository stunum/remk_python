/**
 * 密码哈希测试工具
 * 用于验证前后端密码加密是否一致
 */

import { hashPassword, sha256Hash } from './crypto';
import { PASSWORD_SALT } from '@/config/security';

/**
 * 测试密码哈希
 * @param {string} password 原始密码
 */
export function testPasswordHash(password) {
  console.group('🔐 密码哈希测试');
  
  // 计算哈希
  const hashed = hashPassword(password);
  
  console.log('原始密码:', password);
  console.log('盐值:', PASSWORD_SALT);
  console.log('组合后:', password + PASSWORD_SALT);
  console.log('SHA-256哈希:', hashed);
  console.log('哈希长度:', hashed.length, '(应该是64位十六进制)');
  
  console.groupEnd();
  
  return hashed;
}

/**
 * 生成 Python 测试代码
 * @param {string} password 原始密码
 */
export function generatePythonTestCode(password) {
  const code = `
import hashlib

# 测试密码
password = "${password}"

# 盐值（与前端保持一致）
salt = "${PASSWORD_SALT}"

# 计算哈希
salted = f"{password}{salt}"
hashed = hashlib.sha256(salted.encode('utf-8')).hexdigest()

print(f"原始密码: {password}")
print(f"盐值: {salt}")
print(f"SHA-256哈希: {hashed}")

# 验证密码
def verify_password(plain_password, hashed_password):
    input_hash = hashlib.sha256((plain_password + salt).encode('utf-8')).hexdigest()
    return input_hash == hashed_password

# 测试
is_valid = verify_password(password, hashed)
print(f"密码验证: {'✅ 通过' if is_valid else '❌ 失败'}")
`;
  
  console.log('Python 测试代码:');
  console.log(code);
  
  return code;
}

/**
 * 批量测试密码
 */
export function batchTestPasswords() {
  const testCases = [
    'admin123',
    'doctor123',
    'test1234',
    'Aa123456'
  ];
  
  console.group('📋 批量密码测试');
  
  testCases.forEach(password => {
    const hashed = hashPassword(password);
    console.log(`${password} → ${hashed}`);
  });
  
  console.groupEnd();
}

/**
 * 验证密码匹配
 * @param {string} password 原始密码
 * @param {string} expectedHash 预期的哈希值
 */
export function verifyPasswordHash(password, expectedHash) {
  const actualHash = hashPassword(password);
  const isMatch = actualHash === expectedHash;
  
  console.group(isMatch ? '✅ 密码验证通过' : '❌ 密码验证失败');
  console.log('原始密码:', password);
  console.log('实际哈希:', actualHash);
  console.log('预期哈希:', expectedHash);
  console.log('是否匹配:', isMatch);
  console.groupEnd();
  
  return isMatch;
}

/**
 * 在浏览器控制台中暴露测试函数
 */
if (typeof window !== 'undefined') {
  window.passwordTest = {
    test: testPasswordHash,
    generatePython: generatePythonTestCode,
    batchTest: batchTestPasswords,
    verify: verifyPasswordHash,
    hash: hashPassword,
  };
  
  console.log('💡 密码测试工具已加载，可在控制台使用:');
  console.log('  window.passwordTest.test("你的密码")');
  console.log('  window.passwordTest.generatePython("你的密码")');
  console.log('  window.passwordTest.batchTest()');
  console.log('  window.passwordTest.verify("密码", "预期哈希值")');
}

export default {
  testPasswordHash,
  generatePythonTestCode,
  batchTestPasswords,
  verifyPasswordHash,
};

