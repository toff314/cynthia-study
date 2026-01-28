# 寒假工具集

一个包含日程表管理和阅读题生成器的 Web 应用，采用前后端分离架构。

## 技术栈

### 后端
- Python 3.13
- FastAPI - 高性能异步 Web 框架
- SQLite - 轻量级数据库
- SQLAlchemy - ORM 框架

### 前端
- Vue 3 - 渐进式 JavaScript 框架
- TypeScript - 类型安全的 JavaScript
- Vite - 下一代前端构建工具
- Pinia - Vue 官方状态管理
- Vue Router - 官方路由

## 功能

1. **寒假每日任务日程表** - 管理每日学习任务，记录学习进度
2. **寒假阅读题生成器** - 从 JSON 文件生成阅读理解题

## 快速开始

### 1. 安装后端依赖

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

如果需要使用便捷启动脚本（`start.py` 或 `start_background.py`），还需要安装 `psutil`：

```bash
pip install psutil
```

### 2. 启动后端服务

```bash
# 后端将在 http://localhost:8000 启动
cd backend
python -m uvicorn app.main:app --reload
```

或者简单的使用：

```bash
cd backend
python -m app.main
```

### 3. 安装前端依赖

```bash
cd frontend
npm install
```

### 4. 启动前端开发服务器

```bash
cd frontend
npm run dev
```

前端将在 http://localhost:5173 启动，自动代理 API 请求到后端。

### 5. 访问应用

打开浏览器访问 http://localhost:5173

## 项目结构

```
cynthia-study/
├── backend/                 # 后端项目
│   ├── app/
│   │   ├── main.py         # FastAPI 应用入口
│   │   ├── config.py       # 配置
│   │   ├── database.py     # 数据库连接
│   │   ├── models/         # SQLAlchemy 模型
│   │   ├── schemas/        # Pydantic 模型
│   │   ├── api/            # API 路由
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   ├── data/               # 数据存储目录
│   │   ├── cynthia.db      # SQLite 数据库
│   │   └── quizzes/        # JSON 阅读题文件
│   └── requirements.txt
├── frontend/               # 前端项目
│   ├── src/
│   │   ├── main.ts         # Vue 入口
│   │   ├── App.vue         # 根组件
│   │   ├── api/            # API 调用
│   │   ├── stores/         # Pinia 状态
│   │   ├── views/          # 页面组件
│   │   ├── router/         # 路由配置
│   │   └── types/          # TypeScript 类型
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
└── @read/                  # 旧数据目录（可删除）
```

## API 文档

后端启动后，访问以下地址查看自动生成的 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要 API 端点

#### 健康检查
- `GET /health` - 服务健康状态

#### 日程表管理
- `GET /api/schedule` - 获取日程表数据
- `POST /api/schedule` - 保存日程表数据
- `DELETE /api/schedule` - 清空所有数据

#### 阅读题管理
- `GET /api/quiz/files` - 获取 JSON 文件列表
- `GET /api/quiz/file?name=xxx` - 获取文件内容
- `POST /api/quiz/save` - 保存阅读题

## 生产部署

### 1. 构建前端

```bash
cd frontend
npm run build
```

### 2. 启动后端（生产模式）

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. 快速启动脚本

项目提供了两个便捷的启动脚本：

**`start.py`** - 一键启动脚本（前台运行）:
```bash
python start.py
```

**`start_background.py`** - 后台启动脚本（支持启动/停止/重启）:
```bash
python start_background.py start    # 启动所有服务
python start_background.py stop     # 停止所有服务
python start_background.py restart  # 重启所有服务
python start_background.py status   # 查看服务状态
python start_background.py logs     # 查看所有日志
```

## 数据迁移

原有的 `@read` 目录中的 JSON 文件已自动迁移到 `backend/data/quizzes/` 目录。

## 开发说明

### 后端开发
- Python 版本: 3.13
- 代码风格: PEP 8
- API 文档: 访问 `/docs`

### 前端开发
- Node.js 版本: 18+
- 代码风格: ESLint
- 类型检查: TypeScript

## 许可证

MIT
