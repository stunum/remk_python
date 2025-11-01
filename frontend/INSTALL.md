# 安装和运行指南

## 快速开始

### 1. 安装依赖

```bash
cd frontend
npm install
```

安装过程可能需要几分钟，请耐心等待。

### 2. 选择运行模式

项目支持三种运行模式：

#### 模式一：Web 开发模式（推荐用于前端开发）

```bash
npm run dev
```

- 访问地址：http://localhost:5173
- 适用场景：前端开发、调试
- 特点：快速热更新、浏览器开发者工具

#### 模式二：Electron 开发模式（推荐用于桌面应用开发）

```bash
npm run electron:dev
```

- 运行方式：桌面应用窗口
- 适用场景：桌面应用开发、测试桌面特性
- 特点：完整桌面功能、原生菜单

#### 模式三：Electron 打包模式（用于发布）

```bash
npm run electron:build
```

- 输出目录：`release/`
- 适用场景：生产部署、分发给用户
- 特点：独立可执行文件、无需依赖

## 详细安装步骤

### 系统要求

- **Node.js**: 18.x 或更高版本
- **npm**: 9.x 或更高版本
- **操作系统**: 
  - Windows 10/11 (64位)
  - macOS 10.13 或更高
  - Linux (Ubuntu 18.04+, Debian 10+, Fedora 32+)

### 检查环境

```bash
# 检查 Node.js 版本
node --version
# 应该显示 v18.x.x 或更高

# 检查 npm 版本
npm --version
# 应该显示 9.x.x 或更高
```

### 安装 Node.js（如果需要）

#### Windows

1. 访问 https://nodejs.org/
2. 下载 LTS 版本安装包
3. 运行安装程序，按照向导完成安装

#### macOS

使用 Homebrew：
```bash
brew install node
```

或从官网下载：https://nodejs.org/

#### Linux (Ubuntu/Debian)

```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 克隆项目（如果需要）

```bash
git clone <repository-url>
cd remk_python/frontend
```

### 安装项目依赖

```bash
npm install
```

如果遇到网络问题，可以使用国内镜像：

```bash
# 使用淘宝镜像
npm config set registry https://registry.npmmirror.com
npm install
```

或使用 cnpm：

```bash
npm install -g cnpm --registry=https://registry.npmmirror.com
cnpm install
```

### 配置环境变量

创建 `.env.local` 文件：

```bash
# 复制示例文件（如果有）
cp .env.example .env.local

# 或手动创建
touch .env.local
```

编辑 `.env.local`：

```
VITE_API_BASE_URL=http://localhost:8080/api
```

## 启动后端服务

前端需要连接到 FastAPI 后端服务。

### 启动 FastAPI 后端

```bash
# 在项目根目录
cd /Users/stunum/workspace/eyes/remk_python

# 激活虚拟环境
source .venv/bin/activate

# 启动后端服务
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

确保后端服务运行在 `http://localhost:8080`

## 验证安装

### 1. 启动前端

```bash
npm run dev
```

### 2. 打开浏览器

访问 http://localhost:5173

### 3. 测试功能

- 尝试登录
- 检查网络请求（浏览器开发者工具 > Network）
- 确认能正常连接后端 API

## 常见问题

### 问题 1：npm install 失败

**错误**：`EACCES: permission denied`

**解决**：
```bash
# 不要使用 sudo，而是修复 npm 权限
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.profile
source ~/.profile
```

### 问题 2：端口被占用

**错误**：`Port 5173 is already in use`

**解决**：
```bash
# 方案1：杀死占用端口的进程
# Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:5173 | xargs kill -9

# 方案2：使用其他端口
npm run dev -- --port 5174
```

### 问题 3：无法连接后端

**错误**：`Network Error` 或 `ERR_CONNECTION_REFUSED`

**检查**：
1. 后端服务是否已启动
2. 后端端口是否正确（8080）
3. 防火墙是否阻止连接
4. CORS 是否正确配置

**解决**：
```bash
# 检查后端服务状态
curl http://localhost:8080/api/health

# 如果失败，重启后端服务
```

### 问题 4：Electron 应用白屏

**原因**：
- Vite 开发服务器未启动
- 路径配置错误

**解决**：
```bash
# 确保先启动 Vite 开发服务器
npm run dev

# 在另一个终端启动 Electron
npm run electron:dev
```

### 问题 5：依赖版本冲突

**错误**：`ERESOLVE unable to resolve dependency tree`

**解决**：
```bash
# 清除缓存
npm cache clean --force

# 删除 node_modules 和 package-lock.json
rm -rf node_modules package-lock.json

# 重新安装
npm install --legacy-peer-deps
```

## 更新依赖

### 检查过时的包

```bash
npm outdated
```

### 更新所有依赖

```bash
# 更新到最新兼容版本
npm update

# 更新到最新版本（可能有破坏性更改）
npm install -g npm-check-updates
ncu -u
npm install
```

## 打包发布

### 打包前检查

1. 测试所有功能
2. 更新版本号（package.json）
3. 准备应用图标（build/ 目录）

### 打包命令

```bash
# Windows
npm run electron:build:win

# macOS
npm run electron:build:mac

# Linux
npm run electron:build:linux

# 所有平台（当前系统支持的）
npm run electron:build
```

### 打包输出

打包完成后，在 `release/` 目录查找：

- **Windows**: `.exe` 安装包和便携版
- **macOS**: `.dmg` 磁盘镜像和 `.zip` 压缩包
- **Linux**: `.AppImage` 和 `.deb` 安装包

## 性能优化建议

### 开发环境

1. 使用 SSD 硬盘
2. 增加 Node.js 内存限制：
   ```bash
   export NODE_OPTIONS="--max-old-space-size=4096"
   ```
3. 关闭不必要的开发工具

### 生产环境

1. 使用生产构建：`npm run build`
2. 启用 gzip 压缩
3. 配置 CDN 加速
4. 使用代码分割

## 开发工具推荐

- **VS Code** + Volar 插件（Vue 3）
- **Chrome DevTools** / Firefox Developer Tools
- **Vue DevTools** 浏览器扩展
- **Postman** / **Insomnia** API 测试

## 获取帮助

- 查看 `README.md` - 项目概览
- 查看 `ELECTRON.md` - Electron 详细文档
- 查看 `CONFIG.md` - 配置说明
- 查看 `MIGRATION.md` - 迁移说明

## 下一步

安装完成后，建议：

1. 阅读 `README.md` 了解项目架构
2. 阅读 `ELECTRON.md` 学习 Electron 功能
3. 查看 `src/` 目录熟悉代码结构
4. 运行开发服务器开始开发

祝开发愉快！🎉

