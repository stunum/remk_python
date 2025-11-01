# Wails 到 FastAPI 迁移说明

## 迁移概述

本项目前端原本是 Wails 桌面应用的一部分，现已成功迁移为独立的 Vue 3 + Vite Web 应用，配合 FastAPI 后端使用。

## 迁移完成的工作

### 1. 移除 Wails 相关配置

**文件**: `vite.config.js`

- ✅ 移除了 `process.env.WAILS_DEV` 的 HMR 端口条件判断
- ✅ 移除了 `@wailsjs` 路径别名配置
- ✅ 简化了 HMR 配置，使用标准的 Vite 配置

### 2. 移除 Wails Runtime 导入

**文件**: `src/views/Index.vue`

- ✅ 移除了 `import { Quit } from '../../wailsjs/runtime'`
- ✅ 移除了"关闭程序"菜单项和 `handleClose()` 方法
- ✅ 修复了退出登录逻辑，使用标准的路由跳转

**文件**: `src/views/Login.vue`

- ✅ 移除了 `import { Quit } from '../../wailsjs/runtime/runtime.js'`
- ✅ 移除了"关闭应用程序"按钮
- ✅ 移除了相关的样式定义

**文件**: `src/views/ViewImages.vue`

- ✅ 移除了 Wails Socket 相关注释

**文件**: `src/api/hardware.js`

- ✅ 更新注释，说明通过后端 API 代理调用硬件服务（而非 Wails Go 方法）

### 3. 更新文档

**文件**: `README.md`

- ✅ 完整重写，说明这是 FastAPI + Vue 3 项目
- ✅ 添加了技术栈说明
- ✅ 添加了项目结构说明
- ✅ 添加了开发指南和环境变量配置

## 功能保持

迁移后保持了所有核心功能：

- ✅ 用户登录认证
- ✅ 就诊管理
- ✅ 患者管理
- ✅ 眼底图像采集与查看
- ✅ AI辅助诊断
- ✅ 系统设置
- ✅ 硬件控制（通过后端代理）

## 架构变化

### 之前（Wails 架构）

```
Vue 3 Frontend
    ↓ (Wails Runtime)
Go Backend
    ↓ (HTTP Proxy)
Hardware Service (port 25512)
```

### 现在（FastAPI 架构）

```
Vue 3 Frontend (port 5173)
    ↓ (HTTP API)
FastAPI Backend (port 8080)
    ↓ (HTTP Proxy)
Hardware Service (port 25512)
```

## 开发环境启动

### 后端（FastAPI）

```bash
cd /Users/stunum/workspace/eyes/remk_python
source .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

### 前端（Vue 3）

```bash
cd frontend
npm install
npm run dev
```

前端将在 `http://localhost:5173` 启动，通过 API 调用与后端 `http://localhost:8080` 通信。

## 配置说明

### 环境变量

创建 `frontend/.env.local` 文件：

```
VITE_API_BASE_URL=http://localhost:8080/api
```

### CORS 配置

确保 FastAPI 后端已正确配置 CORS，允许前端域名访问：

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 注意事项

1. **桌面应用特性移除**: 
   - 不再支持"关闭应用"功能（这是桌面应用特性）
   - 用户通过浏览器标签页关闭应用

2. **硬件控制**: 
   - 硬件控制接口保持不变
   - 通过 FastAPI 后端代理访问硬件服务
   - 确保硬件服务运行在端口 25512

3. **认证机制**: 
   - 继续使用 JWT Token 认证
   - Token 存储在 localStorage
   - 通过 Axios 拦截器自动添加到请求头

4. **WebSocket 连接**: 
   - 实时图像传输使用 WebSocket
   - 直接连接到后端 WebSocket 服务

## 验证清单

- ✅ 所有 Wails 相关导入已移除
- ✅ 所有 wailsjs 引用已清理
- ✅ 路由跳转使用标准 Vue Router
- ✅ API 调用通过 Axios 与 FastAPI 后端通信
- ✅ 无 linter 错误
- ✅ 文档已更新

## 迁移完成时间

2025年11月1日

## 后续工作建议

1. 添加 `.env.example` 文件作为环境变量模板
2. 配置生产环境的构建和部署流程
3. 添加 Docker 支持，便于部署
4. 完善 API 错误处理和用户提示

