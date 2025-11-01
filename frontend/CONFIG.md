# 配置说明

## 环境变量配置

### 开发环境

在项目根目录创建 `.env.local` 文件（该文件不会被提交到 Git）：

```bash
# API 基础地址
VITE_API_BASE_URL=http://localhost:8080/api
```

### 生产环境

在项目根目录创建 `.env.production` 文件：

```bash
# API 基础地址（根据实际部署修改）
VITE_API_BASE_URL=https://your-domain.com/api
```

## 后端 API 地址配置

前端通过环境变量 `VITE_API_BASE_URL` 配置后端 API 地址。

默认值（如果未配置）: `http://localhost:8080/api`

## 可用的环境变量

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| VITE_API_BASE_URL | FastAPI 后端 API 基础地址 | http://localhost:8080/api | 否 |

## 开发环境端口

- **前端开发服务器**: http://localhost:5173
- **后端 API 服务器**: http://localhost:8080
- **硬件控制服务**: http://localhost:25512

## CORS 配置

确保后端已正确配置 CORS，允许前端访问：

### FastAPI CORS 配置示例

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # 开发环境
        "https://your-domain.com"  # 生产环境
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 构建配置

### 开发构建

```bash
npm run dev
```

### 生产构建

```bash
npm run build
```

构建产物将输出到 `dist/` 目录。

### 预览生产构建

```bash
npm run preview
```

## 代理配置（可选）

如果需要在开发环境使用代理，可以在 `vite.config.js` 中配置：

```javascript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      }
    }
  }
})
```

这样可以避免 CORS 问题，前端直接请求 `/api/xxx` 会被代理到 `http://localhost:8080/api/xxx`。

