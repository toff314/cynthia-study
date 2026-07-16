# 📚 Cynthia Study - 假期学习助手

> 一个全栈 Web 应用，专为学生假期学习设计，包含日程管理和智能阅读题生成器

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python 3.13](https://img.shields.io/badge/Python-3.13-blue)
![Vue 3](https://img.shields.io/badge/Vue-3-green)
![FastAPI](https://img.shields.io/badge/FastAPI-modern-brightgreen)

## 📖 项目概述

Cynthia Study 是一个现代化的学习管理应用，帮助学生科学安排假期学习计划。通过日程表、成就系统和阅读题生成器，让学习变得更高效、更有趣。

### 🎯 核心功能

| 功能 | 描述 |
|-----|------|
| 📅 **日程管理** | 管理每日学习任务，跟踪学习进度 |
| 📖 **阅读题库** | 基于 JSON 数据自动生成阅读理解题 |
| 🏆 **成就系统** | 记录学习成就，激励持续学习 |
| 📊 **学习统计** | 可视化学习数据，分析学习效果 |
| 🎮 **趣味游戏** | 融合学习与娱乐的小游戏 |

---

## 🛠 技术栈

### 后端技术
- **Python 3.13** - 编程语言
- **FastAPI** - 高性能异步 Web 框架，自动生成 API 文档
- **SQLAlchemy** - ORM 框架，强大的数据库操作
- **SQLite** - 轻量级数据库，开箱即用
- **Pydantic** - 数据验证和序列化

### 前端技术
- **Vue 3** - 渐进式 JavaScript 框架
- **TypeScript** - 类型安全的开发体验
- **Vite** - 下一代前端构建工具，快速热更新
- **Pinia** - 官方状态管理库
- **Vue Router** - 官方路由解决方案

---

## 🚀 快速开始

### 前提条件
- Python 3.13+
- Node.js 18+
- npm 或 yarn

### 后端设置

```bash
# 1. 进入后端目录
cd backend

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动开发服务器
python -m uvicorn app.main:app --reload
```

✅ 后端将在 `http://localhost:8000` 启动

### 前端设置

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev
```

✅ 前端将在 `http://localhost:5173` 启动

### 🌐 访问应用

打开浏览器访问：http://localhost:5173

---

## 📁 项目结构详解

```
cynthia-study/
├── 📂 backend/                    # 后端应用
│   ├── 📂 app/
│   │   ├── main.py               # FastAPI 应用入口
│   │   ├── config.py             # 应用配置
│   │   ├── database.py           # 数据库连接
│   │   ├── 📂 models/            # 数据库模型（SQLAlchemy）
│   │   ├── 📂 schemas/           # 请求/响应模型（Pydantic）
│   │   ├── 📂 api/               # API 路由
│   │   │   ├── achievement.py    # 成就相关接口
│   │   │   ├── game.py           # 游戏相关接口
│   │   │   ├── quiz.py           # 阅读题接口
│   │   │   ├── schedule.py       # 日程表接口
│   │   │   └── statistics.py     # 统计数据接口
│   │   ├── 📂 services/          # 业务逻辑层
│   │   └── 📂 utils/             # 工具函数
│   ├── 📂 data/                  # 数据存储
│   │   ├── cynthia.db            # SQLite 数据库
│   │   └── 📂 quizzes/           # 阅读题 JSON 文件
│   └── requirements.txt           # 依赖列表
│
├── 📂 frontend/                   # 前端应用
│   ├── 📂 src/
│   │   ├── main.ts               # Vue 应用入口
│   │   ├── App.vue               # 根组件
│   │   ├── 📂 api/               # API 请求模块
│   │   ├── 📂 stores/            # Pinia 状态管理
│   │   ├── 📂 views/             # 页面组件
│   │   │   ├── Home.vue          # 首页
│   │   │   ├── Schedule.vue      # 日程表
│   │   │   ├── QuizGenerator.vue # 题库生成器
│   │   │   └── AchievementWall.vue # 成就墙
│   │   ├── 📂 components/        # 可复用组件
│   │   ├── 📂 router/            # 路由配置
│   │   └── 📂 types/             # TypeScript 类型定义
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── @read/                         # 旧数据目录（已迁移，可删除）
├── start.py                       # 一键启动脚本
├── start_background.py            # 后台启动脚本
└── README.md

```

---

## 🔌 API 文档

### 在线文档

后端启动后，自动生成的 API 文档：

| 文档类型 | 地址 |
|---------|------|
| 📊 **Swagger UI** | http://localhost:8000/docs |
| 📘 **ReDoc** | http://localhost:8000/redoc |
| 🔍 **OpenAPI 规范** | http://localhost:8000/openapi.json |

### 主要 API 端点

#### 健康检查
```
GET /health
```

#### 日程表管理
```
GET    /api/schedule           # 获取日程表
POST   /api/schedule           # 保存日程表
DELETE /api/schedule           # 清空所有数据
```

#### 阅读题管理
```
GET  /api/quiz/files           # 获取题库文件列表
GET  /api/quiz/file?name=xxx   # 获取指定文件内容
POST /api/quiz/save            # 保存阅读题
```

#### 成就系统
```
GET /api/achievement           # 获取用户成就
POST /api/achievement          # 添加成就
```

#### 学习统计
```
GET /api/statistics            # 获取统计数据
```

---

## 🚀 快速启动脚本

项目提供了两个便捷启动脚本，无需手动开启多个终端：

### 方式一：前台启动（推荐开发使用）

```bash
python start.py
```

此脚本会：
- ✅ 创建虚拟环境（如需要）
- ✅ 安装后端依赖
- ✅ 启动后端服务（http://localhost:8000）
- ✅ 安装前端依赖
- ✅ 启动前端开发服务器（http://localhost:5173）

### 方式二：后台启动（推荐生产使用）

```bash
# 启动所有服务
python start_background.py start

# 查看服务状态
python start_background.py status

# 查看日志
python start_background.py logs

# 重启服务
python start_background.py restart

# 停止服务
python start_background.py stop
```

---

## 📦 生产部署

### 构建前端

```bash
cd frontend
npm run build
```

生成的静态文件位于 `frontend/dist` 目录。

### 启动后端（生产模式）

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 使用 Docker（可选）

```bash
# 构建镜像
docker build -t cynthia-study .

# 运行容器
docker run -p 8000:8000 -p 5173:5173 cynthia-study
```

---

## 💻 开发指南

### 后端开发

- **编程语言**: Python 3.13
- **代码规范**: PEP 8
- **API 文档**: 自动生成，访问 `/docs`
- **类型检查**: 使用 Pydantic 进行数据验证

**常用命令**：
```bash
# 安装开发依赖
pip install -r requirements.txt

# 运行服务
python -m uvicorn app.main:app --reload

# 格式化代码（可选）
black app/

# 检查代码质量（可选）
flake8 app/
```

### 前端开发

- **框架**: Vue 3（Composition API）
- **编程语言**: TypeScript
- **代码规范**: ESLint
- **构建工具**: Vite
- **Node.js 版本**: 18+

**常用命令**：
```bash
# 安装依赖
npm install

# 启动开发服务器（带热更新）
npm run dev

# 构建生产版本
npm run build

# 预览构建结果
npm run preview

# 检查代码质量
npm run lint
```

---

## 📝 数据说明

### 阅读题数据

原有的 `@read` 目录中的 JSON 文件已自动迁移到 `backend/data/quizzes/` 目录。

**JSON 文件格式**：
```json
{
  "book_name": "书名",
  "questions": [
    {
      "id": 1,
      "question": "问题文本",
      "options": ["选项A", "选项B", "选项C", "选项D"],
      "answer": "正确答案",
      "difficulty": "简单|中等|困难"
    }
  ]
}
```

### 数据库

- **位置**: `backend/data/cynthia.db`
- **类型**: SQLite 3
- **初始化**: 自动创建（首次运行时）

---

## 🐛 故障排除

### 后端启动失败

```
❌ 问题：Port 8000 already in use
✅ 解决：
  # 查找占用端口的进程
  lsof -i :8000
  # 或修改启动端口
  python -m uvicorn app.main:app --port 8001
```

### 前端连接后端失败

```
❌ 问题：CORS error / 网络错误
✅ 解决：
  - 确保后端运行在 localhost:8000
  - 检查 Vite 代理配置（vite.config.ts）
  - 检查浏览器控制台报错信息
```

### 数据库错误

```
❌ 问题：SQLite database is locked
✅ 解决：
  - 关闭其他访问数据库的进程
  - 删除 backend/data/cynthia.db
  - 重新启动应用（自动初始化）
```

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📞 联系方式

有问题或建议？欢迎反馈！

---

**最后更新**: 2026/02/12
