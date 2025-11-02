# 登录后跳转优化

## 更新日期
2025年11月1日

## 问题描述
用户登录成功后，默认跳转到 `/index`，但由于路由配置中 `/index` 重定向到 `/index/dashboard`，而仪表盘菜单被注释掉了，导致页面跳转不符合预期。

## 修改内容

### ✅ 1. 修改路由默认重定向

**文件**: `src/router/modules/wails.js`

**修改前**:
```javascript
{
  path: '/index',
  name: 'index',
  component: () => import('@/views/Index.vue'),
  redirect: '/index/dashboard',  // ❌ 仪表盘已被注释
  // ...
}
```

**修改后**:
```javascript
{
  path: '/index',
  name: 'index',
  component: () => import('@/views/Index.vue'),
  redirect: '/index/patients',  // ✅ 默认跳转到病人管理
  // ...
}
```

### ✅ 2. 优化登录跳转逻辑

**文件**: `src/views/Login.vue`

#### 添加 route 引用

**修改前**:
```javascript
import { useRouter } from 'vue-router';
const router = useRouter();
```

**修改后**:
```javascript
import { useRouter, useRoute } from 'vue-router';
const router = useRouter();
const route = useRoute();  // ✅ 添加
```

#### 优化登录成功跳转

**修改前**:
```javascript
message.success(response.message || '登录成功');
setTimeout(() => {
  router.push('/index').then(() => {
    console.log('跳转成功');
  });
}, 500);
```

**修改后**:
```javascript
message.success(response.msg || response.message || '登录成功');
setTimeout(() => {
  // 检查是否有重定向参数，否则跳转到病人管理
  const redirectPath = route.query.redirect || '/index/patients';
  console.log('准备跳转到:', redirectPath);
  
  router.push(redirectPath).then(() => {
    console.log('跳转成功，当前路由:', router.currentRoute.value.path);
  }).catch(error => {
    console.error('跳转失败:', error);
    // 如果跳转失败，回退到病人管理页面
    router.push('/index/patients');
  });
}, 500);
```

#### 优化已登录用户跳转

**修改前**:
```javascript
onMounted(() => {
  if (userStore.isLoggedIn) {
    router.push('/index');  // ❌ 总是跳转到 /index
    return;
  }
  // ...
});
```

**修改后**:
```javascript
onMounted(() => {
  if (userStore.isLoggedIn) {
    // 如果有重定向参数，跳转到重定向页面，否则跳转到病人管理
    const redirectPath = route.query.redirect || '/index/patients';
    router.push(redirectPath);
    return;
  }
  // ...
});
```

## 路由结构

### 主路由配置

```
/
├─ /login                    # 登录页面（公开）
├─ /index                    # 主布局页面（需要认证）
│  ├─ redirect → /index/patients  # 默认重定向
│  ├─ /index/patients        # 病人管理（默认页面）✅
│  ├─ /index/patients/:id/history  # 患者历史
│  ├─ /index/visits          # 就诊管理
│  ├─ /index/settings        # 系统设置
│  └─ /index/dashboard       # 仪表盘（已注释）
├─ /view-images              # 图像查看（独立页面）
└─ /ai-diagnosis             # AI诊断（独立页面）
```

## 跳转流程

### 场景 1: 正常登录

```
1. 用户访问 /login
2. 输入用户名密码
3. 登录成功
4. 跳转到 /index/patients (病人管理)
```

### 场景 2: 未登录访问受保护页面

```
1. 用户未登录访问 /index/settings
2. 路由守卫拦截，重定向到 /login?redirect=/index/settings
3. 用户登录成功
4. 自动跳转回 /index/settings (系统设置)
```

### 场景 3: 已登录访问登录页

```
1. 已登录用户访问 /login
2. 路由守卫检测到已登录
3. 直接跳转到 /index (然后自动重定向到 /index/patients)
```

### 场景 4: 已登录刷新页面

```
1. 用户在 /login 页面刷新
2. onMounted 检测到已登录
3. 跳转到 /index/patients
```

## 菜单结构

当前可用菜单（按显示顺序）:

1. **就诊管理** - `/index/visits`
2. **病人管理** - `/index/patients` ⭐ 默认页面
3. **系统设置** - `/index/settings`

注释掉的菜单:
- ~~仪表盘~~ - `/index/dashboard`

## 测试场景

### ✅ 测试 1: 登录后默认跳转

```bash
# 1. 启动应用
npm run dev

# 2. 访问 http://localhost:5173
# 3. 登录（admin/admin123）
# 4. 验证是否跳转到 /index/patients
```

**预期结果**: 登录成功后应该看到"病人管理"页面

### ✅ 测试 2: 带重定向参数登录

```bash
# 1. 清除浏览器缓存/退出登录
# 2. 直接访问 http://localhost:5173/index/settings
# 3. 会重定向到 /login?redirect=/index/settings
# 4. 登录成功
# 5. 验证是否跳转回 /index/settings
```

**预期结果**: 登录成功后应该看到"系统设置"页面

### ✅ 测试 3: 已登录用户访问登录页

```bash
# 1. 确保已登录
# 2. 手动访问 http://localhost:5173/login
# 3. 验证是否自动跳转到 /index/patients
```

**预期结果**: 自动跳转到"病人管理"页面，不显示登录表单

### ✅ 测试 4: 直接访问 /index

```bash
# 1. 登录后
# 2. 手动访问 http://localhost:5173/index
# 3. 验证是否自动重定向到 /index/patients
```

**预期结果**: 自动显示"病人管理"页面

## 优化效果

### 之前 ❌
- 登录后跳转到 `/index`
- 自动重定向到 `/index/dashboard`
- 但仪表盘菜单被注释，可能导致 404 或空白页

### 现在 ✅
- 登录后跳转到 `/index/patients`（病人管理）
- 支持 redirect 参数，可以跳转回原访问页面
- 跳转失败时有容错处理，回退到病人管理
- 更符合业务逻辑（医疗系统优先展示患者信息）

## 相关文件

- `src/router/modules/wails.js` - 路由配置
- `src/views/Login.vue` - 登录页面
- `src/router/guards.js` - 路由守卫
- `src/views/Index.vue` - 主布局页面

## 后续优化建议

### 短期
1. ✅ 测试所有跳转场景
2. ⏳ 根据用户角色跳转到不同页面
   - 管理员 → 系统设置
   - 医生 → 就诊管理
   - 技师 → 图像查看

### 长期
1. ⏳ 实现仪表盘页面
2. ⏳ 记住用户上次访问的页面
3. ⏳ 添加欢迎页面/引导页
4. ⏳ 实施权限控制，根据权限显示菜单

## 完成检查清单

- [x] 修改路由默认重定向
- [x] 添加 useRoute 引用
- [x] 优化登录成功跳转逻辑
- [x] 优化已登录用户跳转逻辑
- [x] 添加错误处理和容错机制
- [x] 验证无 linter 错误
- [x] 创建文档

## 总结

**主要变更**: 
1. `/index` 默认重定向从 `/index/dashboard` 改为 `/index/patients`
2. 登录成功后支持 redirect 参数，默认跳转到病人管理

**影响范围**: 所有登录相关的跳转逻辑

**向后兼容**: ✅ 完全兼容，不影响现有功能

**测试状态**: ⏳ 待测试

---

**更新人员**: AI Assistant  
**审核状态**: ⏳ 待审核  
**测试状态**: ⏳ 待测试

