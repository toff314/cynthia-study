# 绘本阅读模块设计方案

> 状态：已批准  
> 设计日期：2026-07-15  
> 相关技能：brainstorming、coding-harness

## 1. 需求概述

为 Cynthia Study 增加一个「绘本阅读」模块：

- 在首页展示入口卡片。
- 进入后显示云端绘本目录树，默认根路径为 `/团团园圆/绘本/【1】3000套中文绘本（67G）`。
- 目录树实时响应，展开到最底层时列出可阅读的绘本文件（PDF/PPT）。
- 点击绘本文件名后，从云端下载该文件并转换为图片，在全屏阅读器中展示。
- 支持打印当前绘本的所有图片。
- 不持久化保存下载文件：仅在点击阅读时产生临时缓存，并通过每日 crontab 清理。
- 用户界面不暴露「百度网盘」，统一使用「云端/在线」概念。
- 遵循 `DESIGN.md` 的视觉与交互规范。

## 2. 架构设计

```
┌─────────────────┐     ┌─────────────────────────────┐     ┌──────────────┐
│ 前端 Vue 3      │     │ 后端 FastAPI                │     │ 百度网盘     │
│                 │     │                             │     │ (后端实现)   │
│ Home.vue        │     │ /api/reading/list           │     │              │
│ Reading.vue     │────▶│ /api/reading/read           │────▶│ BaiduPCSClient│
│ Reader.vue      │◀────│ /api/reading/images/{tid}/{p}│     │              │
└─────────────────┘     │ /api/reading/cleanup          │     └──────────────┘
                        └─────────────────────────────┘
                                        │
                                        ▼
                        backend/data/cache/reading/
                        (临时 PDF/PPT 与转换后的图片)
```

## 3. 页面与路由

### 3.1 首页入口

- 在 `Home.vue` 的 `tools-container` 中新增一个工具卡片。
- emoji：`📖`
- 标题：「绘本阅读」
- 描述：「从云端读取绘本，在线全屏阅读，支持打印」
- 颜色：青色 `{colors.primary-teal}`，`card-teal` 作为 hover/选中背景参考。
- 路由：`/reading`

### 3.2 阅读模块页面 `/reading`

- 遵循子页面规范：渐变背景、白色大圆角内容卡片、返回首页、左侧 QuickNav。
- 页面标题：`📖 绘本阅读`
- 页面内容：
  - 左侧：Element Plus `el-tree` 树形目录，默认展开根路径，懒加载或一次性加载。
  - 右侧：文件列表，展示当前选中目录下的 PDF/PPT 文件。
  - 点击文件：触发后端转换，打开全屏阅读器。

### 3.3 全屏阅读器

- 全屏覆盖层，隐藏 QuickNav、返回按钮、操作栏。
- 展示当前绘本的所有图片，左右翻页。
- 键盘支持：`←` / `→` 翻页，`Esc` 退出。
- 打印按钮：打印所有图片。
- 图片自适应：`max-width: 100%`、`max-height: 100vh`、`object-fit: contain`。
- 不同 PDF/PPT 尺寸统一自适应容器。

## 4. 后端 API 设计

### 4.1 列出目录

```http
GET /api/reading/list?path={path}
```

- `path`：云端路径，默认根路径。
- 响应：

```json
{
  "success": true,
  "data": [
    { "name": "分类A", "path": "/.../分类A", "is_dir": true },
    { "name": "绘本1.pdf", "path": "/.../绘本1.pdf", "is_dir": false, "size": 123456 }
  ]
}
```

### 4.2 阅读转换

```http
POST /api/reading/read
Content-Type: application/json

{ "path": "/.../绘本1.pdf" }
```

- 后端行为：
  1. 校验配置是否可用。
  2. 从云端下载文件到临时目录 `backend/data/cache/reading/{task_id}/`。
  3. 转换为图片：
     - PDF：使用 `pymupdf` 直接转 PNG。
     - PPT：使用 LibreOffice headless 转 PDF，再使用 `pymupdf` 转 PNG。
  4. 返回任务 ID 与页数。

- 响应：

```json
{
  "success": true,
  "data": {
    "task_id": "uuid",
    "pages": 24,
    "image_urls": ["/api/reading/images/uuid/1", "..."]
  }
}
```

### 4.3 读取图片

```http
GET /api/reading/images/{task_id}/{page}
```

- 返回对应页码的 PNG 图片。

### 4.4 手动清理

```http
POST /api/reading/cleanup
```

- 删除 `backend/data/cache/reading/` 下所有临时目录与文件。
- 用于测试或手动释放空间。

## 5. 百度网盘集成

### 5.1 配置文件

- 使用独立配置，不直接依赖 libretv-enhanced。
- 配置文件路径：`~/.config/cynthia-study/baidu_config.json`
- 配置字段与 libretv-enhanced 保持一致：

```json
{
  "baidu_cookies": "",
  "baidu_bduss": "",
  "baidu_stoken": ""
}
```

- 用户可从 libretv-enhanced 的 `~/.config/cli-anything-tvdown/config.json` 复制对应字段。

### 5.2 BaiduPCSClient

- 将 libretv-enhanced 的 `BaiduPCSClient` 实现复制到 `backend/app/services/baidu_pcs.py`。
- 仅复用 `list_dir` 与下载能力；如需下载，可复用其 session 与 cookies 机制，通过 `https://pan.baidu.com/api/download` 或类似接口获取下载链接。
- 在 `backend/app/services/reading_service.py` 中封装绘本业务逻辑，避免 API 路由直接调用 `BaiduPCSClient`。

## 6. 文件转换

### 6.1 临时目录结构

```
backend/data/cache/reading/
└── {task_id}/
    ├── source.pdf   (或 source.ppt)
    └── page_1.png
    └── page_2.png
    └── ...
```

### 6.2 转换流程

1. 下载文件：云端路径 -> `source.pdf` 或 `source.ppt`。
2. 如果源文件是 PPT：
   - 调用 `libreoffice --headless --convert-to pdf --outdir ... source.ppt`。
   - 得到 `source.pdf`。
3. 使用 `pymupdf` 将 PDF 逐页转为 PNG。
4. 删除中间产物（如 PPT 转换后的 PDF 和原始 PPT），保留 PNG。

### 6.3 依赖

- Python：`pymupdf`、`requests`、`requests-toolbelt`、`urllib3`
- 系统：`libreoffice`（soffice/libreoffice）

## 7. 清理任务

### 7.1 清理脚本

- 文件：`backend/scripts/cleanup_reading_cache.py`
- 功能：递归删除 `backend/data/cache/reading/` 下所有内容。
- 可通过 `python backend/scripts/cleanup_reading_cache.py` 手动执行，也可由 crontab 调用。

### 7.2 crontab

- 每日凌晨执行一次。
- 示例：

```cron
0 3 * * * cd /home/yuanwu/cynthia-study && /home/yuanwu/cynthia-study/backend/venv/bin/python backend/scripts/cleanup_reading_cache.py >> /home/yuanwu/cynthia-study/logs/reading_cleanup.log 2>&1
```

## 8. 错误处理

- 凭证未配置：返回明确的错误信息，前端提示用户配置。
- 路径不存在：返回 404。
- 转换失败：记录日志，返回 500，前端显示错误。
- 下载超时：设置合理超时，前端展示 loading 状态。

## 9. 测试策略

1. 使用 `@read/` 目录下的本地 PDF/PPT 文件做 fallback 测试，验证转换与阅读流程。
2. 配置百度凭证后，测试真实网盘的目录列表与下载。
3. 测试全屏阅读、左右翻页、打印、ESC 退出。
4. 测试清理脚本能否正确删除临时文件。

## 10. 风险与依赖

- **LibreOffice 安装**：目标环境必须可用 `soffice`/`libreoffice` 命令。
- **大文件转换耗时**：大 PDF/PPT 转换可能较慢，前端需显示 loading。
- **百度网盘 API 限制**：访问频率、下载速度受限，需做好超时与重试。
- **空间占用**：临时缓存可能占用较大磁盘，清理任务必须稳定运行。

## 11. 影响文件

### 后端
- `backend/app/main.py`：注册 reading 路由
- `backend/app/api/reading.py`：新增路由
- `backend/app/services/reading_service.py`：绘本业务逻辑
- `backend/app/services/baidu_pcs.py`：百度网盘客户端
- `backend/app/config.py`：新增缓存目录、配置路径
- `backend/requirements.txt`：新增依赖
- `backend/scripts/cleanup_reading_cache.py`：清理脚本

### 前端
- `frontend/src/views/Home.vue`：新增入口卡片
- `frontend/src/views/Reading.vue`：阅读模块页面
- `frontend/src/components/Reader.vue`：全屏阅读器
- `frontend/src/router/index.ts`：新增 `/reading` 路由
- `frontend/src/api/reading.ts`：API 请求
- `frontend/src/components/QuickNav.vue`：新增阅读入口
