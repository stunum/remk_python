# Electron 桌面应用打包指南

## 概述

本项目支持打包成桌面应用，使用 Electron + Vue 3 + Vite 技术栈。

## 环境要求

- Node.js 18+ 
- npm 9+
- 操作系统：
  - Windows 10/11 (x64)
  - macOS 10.13+ (Intel/Apple Silicon)
  - Linux (x64)

## 项目结构

```
frontend/
├── electron/              # Electron 主进程代码
│   ├── main.js           # 主进程入口
│   └── preload.js        # 预加载脚本
├── src/                  # Vue 应用源码
├── build/                # 打包资源（图标等）
│   ├── icon.ico         # Windows 图标
│   ├── icon.icns        # macOS 图标
│   └── icon.png         # Linux 图标
├── dist/                 # 构建输出
└── release/              # 打包输出
```

## 开发模式

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

#### 方式一：Web 模式（浏览器）

```bash
npm run dev
```

访问 http://localhost:5173

#### 方式二：Electron 模式（桌面应用）

```bash
npm run electron:dev
```

这会同时启动：
- Vite 开发服务器 (端口 5173)
- Electron 桌面应用（加载开发服务器）

### 开发模式特性

- ✅ 热模块替换 (HMR)
- ✅ 自动重载
- ✅ 开发者工具
- ✅ 源码调试

## 生产打包

### 准备工作

1. **准备图标文件**

将应用图标放在 `build/` 目录：
- `icon.ico` - Windows (256x256)
- `icon.icns` - macOS (512x512)
- `icon.png` - Linux (512x512)

可以使用在线工具转换：
- https://www.icoconverter.com/ (ICO)
- https://iconverticons.com/ (ICNS)

2. **配置应用信息**

编辑 `package.json` 中的 `build` 配置：

```json
{
  "build": {
    "appId": "com.remk.eyes.examination",
    "productName": "瑞尔明康眼底检查系统",
    "copyright": "Copyright © 2025 瑞尔明康"
  }
}
```

### 打包命令

#### 打包所有平台（当前系统）

```bash
npm run electron:build
```

#### 打包 Windows 版本

```bash
npm run electron:build:win
```

输出文件：
- `release/remk-eyes-examination Setup x.x.x.exe` (安装包)
- `release/remk-eyes-examination x.x.x.exe` (便携版)

#### 打包 macOS 版本

```bash
npm run electron:build:mac
```

输出文件：
- `release/remk-eyes-examination-x.x.x.dmg` (磁盘镜像)
- `release/remk-eyes-examination-x.x.x-mac.zip` (压缩包)

#### 打包 Linux 版本

```bash
npm run electron:build:linux
```

输出文件：
- `release/remk-eyes-examination-x.x.x.AppImage` (AppImage)
- `release/remk-eyes-examination_x.x.x_amd64.deb` (Debian/Ubuntu)

### 跨平台打包

如需在一个平台打包其他平台的应用，需要额外配置：

**在 macOS 上打包 Windows/Linux**：支持  
**在 Windows 上打包 macOS**：需要配置  
**在 Linux 上打包 macOS**：需要配置

参考：https://www.electron.build/multi-platform-build

## Electron API 使用

### 在 Vue 组件中使用

```javascript
import { isElectron, electronApp, electronDialog } from '@/utils/electron';

// 检查是否在 Electron 环境
if (isElectron()) {
  // 获取应用版本
  const version = await electronApp.getVersion();
  
  // 显示保存对话框
  const result = await electronDialog.showSaveDialog({
    title: '保存文件',
    defaultPath: 'image.png',
    filters: [
      { name: 'Images', extensions: ['png', 'jpg'] }
    ]
  });
  
  // 退出应用
  await electronApp.quit();
}
```

### 可用的 API

#### 应用控制
- `electronApp.quit()` - 退出应用
- `electronApp.getVersion()` - 获取版本
- `electronApp.getPath(name)` - 获取系统路径

#### 对话框
- `electronDialog.showSaveDialog(options)` - 保存对话框
- `electronDialog.showOpenDialog(options)` - 打开对话框
- `electronDialog.showMessageBox(options)` - 消息框

#### 窗口控制
- `electronWindow.minimize()` - 最小化
- `electronWindow.maximize()` - 最大化/还原
- `electronWindow.close()` - 关闭窗口
- `electronWindow.isMaximized()` - 是否最大化

## 配置说明

### 窗口配置

编辑 `electron/main.js`：

```javascript
const mainWindow = new BrowserWindow({
  width: 1400,        // 宽度
  height: 900,        // 高度
  minWidth: 1200,     // 最小宽度
  minHeight: 768,     // 最小高度
  title: '应用标题',
  icon: 'path/to/icon.png',
  // 更多配置...
});
```

### 打包配置

编辑 `package.json` 中的 `build` 部分：

```json
{
  "build": {
    "appId": "com.your.app",
    "productName": "应用名称",
    "files": [
      "dist/**/*",
      "electron/**/*"
    ],
    "directories": {
      "output": "release"
    }
  }
}
```

## 兼容性

### Web 和 Electron 双模式

项目支持同时作为 Web 应用和 Electron 应用运行：

**Web 模式**：
```bash
npm run dev      # 开发
npm run build    # 构建
```

**Electron 模式**：
```bash
npm run electron:dev     # 开发
npm run electron:build   # 打包
```

代码会自动检测运行环境：

```javascript
if (isElectron()) {
  // Electron 特定功能
  await electronApp.quit();
} else {
  // Web 浏览器功能
  window.close();
}
```

## 常见问题

### 1. 打包后白屏

**原因**：路径配置错误

**解决**：确保 `vite.config.js` 中设置了正确的 base：

```javascript
export default defineConfig(({ mode }) => ({
  base: mode === 'production' ? './' : '/',
}));
```

### 2. 无法加载本地资源

**原因**：CSP 或路径问题

**解决**：检查 `electron/main.js` 中的 `webPreferences`：

```javascript
webPreferences: {
  nodeIntegration: false,
  contextIsolation: true,
  webSecurity: true,
}
```

### 3. Electron API 未定义

**原因**：预加载脚本未正确加载

**解决**：
1. 确认 `preload.js` 路径正确
2. 检查 `contextBridge` 是否正确暴露 API
3. 在组件中使用前检查 `isElectron()`

### 4. 打包体积过大

**解决方案**：

1. 使用代码分割（已在 vite.config.js 配置）
2. 移除未使用的依赖
3. 配置 asar 压缩：

```json
{
  "build": {
    "asar": true,
    "asarUnpack": ["**/*.node"]
  }
}
```

### 5. macOS 签名和公证

macOS 发布需要签名和公证：

```json
{
  "build": {
    "mac": {
      "identity": "Developer ID Application: Your Name (TEAM_ID)",
      "hardenedRuntime": true,
      "gatekeeperAssess": false,
      "entitlements": "build/entitlements.mac.plist",
      "entitlementsInherit": "build/entitlements.mac.plist"
    },
    "afterSign": "scripts/notarize.js"
  }
}
```

## 性能优化

### 1. 减小包体积

- 使用 `asar` 压缩
- 配置文件过滤
- 移除开发依赖

### 2. 加快启动速度

- 延迟加载非关键模块
- 使用 V8 快照
- 优化窗口创建

### 3. 降低内存占用

- 及时释放大对象
- 使用 Worker 处理密集任务
- 配置 Node.js 内存限制

## 调试技巧

### 主进程调试

```bash
# 启用 Node.js 调试
cross-env NODE_OPTIONS='--inspect=5858' npm run electron:dev
```

在 Chrome 中打开 `chrome://inspect`

### 渲染进程调试

Electron 应用中按 `Ctrl+Shift+I` (Windows/Linux) 或 `Cmd+Option+I` (macOS) 打开开发者工具。

### 查看日志

```javascript
// 主进程日志
console.log('Main process log');

// 渲染进程日志（在开发者工具中查看）
console.log('Renderer process log');
```

## 发布流程

1. **更新版本号** - 编辑 `package.json`
2. **测试应用** - 运行 `npm run electron:dev`
3. **构建打包** - 运行 `npm run electron:build`
4. **测试安装包** - 在目标系统上测试
5. **发布** - 上传到服务器或应用商店

## 自动更新

可以集成 `electron-updater` 实现自动更新：

```bash
npm install electron-updater
```

配置参考：https://www.electron.build/auto-update

## 相关资源

- [Electron 官方文档](https://www.electronjs.org/docs)
- [Electron Builder 文档](https://www.electron.build/)
- [Vite 官方文档](https://vitejs.dev/)
- [Vue 3 官方文档](https://vuejs.org/)

## 技术支持

如有问题，请查看：
- 项目 README.md
- MIGRATION.md（迁移文档）
- CONFIG.md（配置文档）

