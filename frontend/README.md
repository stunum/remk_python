# 瑞尔明康眼底检查系统 - 前端

基于 Vue 3 + Vite 的现代化前端应用，配合 FastAPI 后端提供完整的眼底检查系统解决方案。

## 技术栈

- **框架**: Vue 3 (Composition API + `<script setup>`)
- **构建工具**: Vite
- **UI 组件库**: 
  - Ant Design Vue (主要UI组件)
  - Element Plus (表单和辅助组件)
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP 客户端**: Axios
- **样式**: SCSS

## 项目结构

```
src/
├── api/              # API 接口定义
├── assets/           # 静态资源
├── components/       # 可复用组件
├── router/           # 路由配置
├── store/            # Pinia 状态管理
├── styles/           # 全局样式
├── utils/            # 工具函数
├── views/            # 页面组件
└── workers/          # Web Workers
```

## 开发指南

### 安装依赖

```bash
npm install
```

### 运行模式

项目支持两种运行模式：

#### Web 模式（浏览器）

```bash
# 开发环境
npm run dev

# 生产构建
npm run build

# 预览生产构建
npm run preview
```

应用将在 `http://localhost:5173` 启动

#### Electron 模式（桌面应用）

```bash
# 开发环境
npm run electron:dev

# 打包应用
npm run electron:build          # 打包所有平台
npm run electron:build:win      # 仅打包 Windows
npm run electron:build:mac      # 仅打包 macOS
npm run electron:build:linux    # 仅打包 Linux
```

详细说明请查看 [ELECTRON.md](./ELECTRON.md) 和 [INSTALL.md](./INSTALL.md)

## 环境变量

创建 `.env.local` 文件配置 API 地址：

```
VITE_API_BASE_URL=http://localhost:8080/api
```

## 推荐开发工具

- [VS Code](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar)

## 主要功能模块

- 用户登录认证
- 就诊管理
- 患者管理
- 眼底图像采集与查看
- AI辅助诊断
- 系统设置

## 与后端集成

本前端应用与 FastAPI 后端配合使用，通过 RESTful API 进行数据交互。确保后端服务已启动并运行在配置的 API 地址上。

## 桌面应用打包

项目支持使用 Electron 打包成桌面应用，支持 Windows、macOS、Linux 平台。

**快速开始**：
```bash
# 开发模式
npm run electron:dev

# 打包发布
npm run electron:build
```

**详细文档**：
- [ELECTRON.md](./ELECTRON.md) - Electron 完整指南
- [INSTALL.md](./INSTALL.md) - 安装和运行指南
- [CONFIG.md](./CONFIG.md) - 配置说明

## 相关文档

- [README.md](./README.md) - 项目概览（当前文档）
- [ELECTRON.md](./ELECTRON.md) - Electron 桌面应用打包指南
- [INSTALL.md](./INSTALL.md) - 详细安装和运行说明
- [CONFIG.md](./CONFIG.md) - 环境变量和配置说明
- [MIGRATION.md](./MIGRATION.md) - 从 Wails 迁移说明
