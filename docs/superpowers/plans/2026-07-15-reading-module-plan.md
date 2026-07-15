# 绘本阅读模块实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: 建议直接在当前会话按任务顺序执行，每个任务完成后验证再进入下一个。

**Goal:** 在 Cynthia Study 中新增一个「绘本阅读」模块，从百度网盘读取 PDF/PPT 绘本并转换为图片，在线全屏阅读、支持打印，每日自动清理临时文件。

**Architecture:** 后端 FastAPI 封装百度网盘客户端与文件转换逻辑，前端 Vue 3 提供树形目录、文件列表和全屏阅读器。点击阅读时才下载并转换；临时文件通过独立 crontab 脚本每日清理。

**Tech Stack:** Python 3.13 + FastAPI + pymupdf + requests + LibreOffice；Vue 3 + Element Plus + TypeScript + Axios。

---

## 文件总览

### 后端新增/修改
- `backend/app/services/baidu_pcs.py`：复制 BaiduPCSClient，提供 list_dir / download。
- `backend/app/services/reading_service.py`：绘本业务：目录列表、下载、转换、清理。
- `backend/app/api/reading.py`：FastAPI 路由 `/api/reading/*`。
- `backend/app/config.py`：新增 `READING_CACHE_DIR`、配置路径。
- `backend/app/main.py`：注册 reading 路由。
- `backend/scripts/cleanup_reading_cache.py`：清理脚本。
- `backend/requirements.txt`：新增 `pymupdf`、`requests`、`requests-toolbelt`、`urllib3`。

### 前端新增/修改
- `frontend/src/api/reading.ts`：封装 reading API。
- `frontend/src/views/Reading.vue`：绘本阅读页面（目录树 + 文件列表）。
- `frontend/src/components/Reader.vue`：全屏阅读器组件。
- `frontend/src/views/Home.vue`：新增入口卡片。
- `frontend/src/router/index.ts`：新增 `/reading` 路由。
- `frontend/src/components/QuickNav.vue`：新增阅读入口。

---

## Task 1: 后端依赖与配置

**Files:**
- Modify: `backend/requirements.txt`
- Modify: `backend/app/config.py`

- [ ] **Step 1: 添加依赖**

在 `backend/requirements.txt` 末尾追加：

```
pymupdf==1.24.10
requests==2.32.3
requests-toolbelt==1.0.0
urllib3==2.2.3
```

- [ ] **Step 2: 在虚拟环境中安装依赖**

```bash
cd /home/yuanwu/cynthia-study/backend
source venv/bin/activate
pip install pymupdf==1.24.10 requests==2.32.3 requests-toolbelt==1.0.0 urllib3==2.2.3
```

- [ ] **Step 3: 更新配置类**

在 `backend/app/config.py` 的 `Settings` 类中追加：

```python
    # 绘本阅读模块配置
    READING_CACHE_DIR: Path = BASE_DIR / "data" / "cache" / "reading"
    READING_CONFIG_DIR: Path = Path.home() / ".config" / "cynthia-study"
    READING_CONFIG_FILE: Path = READING_CONFIG_DIR / "baidu_config.json"
    READING_ROOT_PATH: str = "/团团园圆/绘本/【1】3000套中文绘本（67G）"
```

并确保 `READING_CACHE_DIR` 在 `__init__` 或类定义时创建：

```python
    READING_CACHE_DIR.mkdir(parents=True, exist_ok=True)
```

---

## Task 2: 百度网盘客户端

**Files:**
- Create: `backend/app/services/baidu_pcs.py`

- [ ] **Step 1: 复制并精简 BaiduPCSClient**

从 `/home/yuanwu/libretv-enhanced/tv-download-cli/agent-harness/internal/core/baidu_pcs.py` 复制核心代码到 `backend/app/services/baidu_pcs.py`。保留 `__init__`、`list_dir`、`file_exists`、下载相关方法；删除上传相关方法（upload_slice、precreate、upload_file 等）。

- [ ] **Step 2: 增加下载方法**

在 `BaiduPCSClient` 中新增 `download_file(path: str, local_path: str) -> bool`：

1. 通过 `https://pan.baidu.com/api/download` 获取下载链接。
2. 用 session 下载到 `local_path`。
3. 返回是否成功。

具体实现需参考 libretv-enhanced 中类似下载逻辑或自行构造请求参数：`path`、`bdstoken`、`app_id`。

- [ ] **Step 3: 提供独立配置读取函数**

在 `backend/app/services/baidu_pcs.py` 末尾新增：

```python
def load_baidu_config() -> dict:
    """读取 ~/.config/cynthia-study/baidu_config.json"""
    config_file = settings.READING_CONFIG_FILE
    if config_file.exists():
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def create_baidu_client() -> BaiduPCSClient:
    config = load_baidu_config()
    return BaiduPCSClient(
        cookies=config.get("baidu_cookies") or None,
        bduss=config.get("baidu_bduss") or None,
        stoken=config.get("baidu_stoken") or None,
    )
```

- [ ] **Step 4: 测试 list_dir 能否在配置存在时工作**

先创建一个空的测试配置文件（不填凭证），验证未配置时抛出 BaiduPCSError 或返回友好提示。

---

## Task 3: 阅读业务服务

**Files:**
- Create: `backend/app/services/reading_service.py`

- [ ] **Step 1: 创建目录列表函数**

```python
def list_reading_directory(path: str | None = None) -> list[dict]:
    """列出云端目录内容。path 为 None 时使用默认根路径。"""
    client = create_baidu_client()
    target_path = path or settings.READING_ROOT_PATH
    items = client.list_dir(target_path)
    return [
        {
            "name": item.get("server_filename"),
            "path": item.get("path"),
            "is_dir": item.get("isdir") == 1,
            "size": item.get("size"),
        }
        for item in items
    ]
```

- [ ] **Step 2: 创建下载与转换函数**

```python
def convert_to_images(remote_path: str) -> dict:
    """下载远程文件并转换为图片，返回 task_id 与页数。"""
    task_id = str(uuid.uuid4())
    task_dir = settings.READING_CACHE_DIR / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    
    ext = Path(remote_path).suffix.lower()
    source_file = task_dir / f"source{ext}"
    
    client = create_baidu_client()
    client.download_file(remote_path, str(source_file))
    
    pdf_file = source_file
    if ext in (".ppt", ".pptx"):
        pdf_file = _convert_ppt_to_pdf(source_file, task_dir)
    
    pages = _convert_pdf_to_images(pdf_file, task_dir)
    
    # 清理中间产物，只保留图片
    if source_file.exists():
        source_file.unlink()
    if pdf_file != source_file and pdf_file.exists():
        pdf_file.unlink()
    
    return {
        "task_id": task_id,
        "pages": pages,
    }
```

- [ ] **Step 3: 实现 PPT 转 PDF**

```python
def _convert_ppt_to_pdf(ppt_file: Path, output_dir: Path) -> Path:
    cmd = [
        "soffice",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", str(output_dir),
        str(ppt_file),
    ]
    subprocess.run(cmd, check=True, timeout=300)
    return output_dir / f"{ppt_file.stem}.pdf"
```

- [ ] **Step 4: 实现 PDF 转图片**

```python
def _convert_pdf_to_images(pdf_file: Path, output_dir: Path) -> int:
    doc = fitz.open(str(pdf_file))
    for i in range(len(doc)):
        page = doc.load_page(i)
        # 2x 分辨率，保证清晰
        pix = page.get_pixmap(dpi=150)
        pix.save(str(output_dir / f"page_{i+1}.png"))
    return len(doc)
```

- [ ] **Step 5: 实现图片读取与清理**

```python
def get_image_path(task_id: str, page: int) -> Path:
    return settings.READING_CACHE_DIR / task_id / f"page_{page}.png"


def cleanup_reading_cache() -> None:
    """删除所有临时缓存。"""
    import shutil
    if settings.READING_CACHE_DIR.exists():
        shutil.rmtree(settings.READING_CACHE_DIR)
    settings.READING_CACHE_DIR.mkdir(parents=True, exist_ok=True)
```

- [ ] **Step 6: 用本地 @read 文件测试转换**

临时写一个小脚本调用 `convert_to_images` 的本地版本，验证 PDF/PPT 能正确生成 PNG。

---

## Task 4: 后端 API 路由

**Files:**
- Create: `backend/app/api/reading.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 创建 reading 路由**

```python
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from app.services.reading_service import (
    list_reading_directory,
    convert_to_images,
    get_image_path,
    cleanup_reading_cache,
)
from app.services.baidu_pcs import BaiduPCSError

router = APIRouter(prefix="/reading", tags=["reading"])


class ReadRequest(BaseModel):
    path: str


@router.get("/list")
def api_list(path: str | None = None):
    try:
        items = list_reading_directory(path)
        return {"success": True, "data": items}
    except BaiduPCSError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/read")
def api_read(req: ReadRequest):
    try:
        result = convert_to_images(req.path)
        return {
            "success": True,
            "data": {
                "task_id": result["task_id"],
                "pages": result["pages"],
                "image_urls": [
                    f"/api/reading/images/{result['task_id']}/{i}"
                    for i in range(1, result["pages"] + 1)
                ],
            },
        }
    except BaiduPCSError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/images/{task_id}/{page}")
def api_image(task_id: str, page: int):
    image_path = get_image_path(task_id, page)
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(str(image_path), media_type="image/png")


@router.post("/cleanup")
def api_cleanup():
    try:
        cleanup_reading_cache()
        return {"success": True, "message": "Cleanup completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

- [ ] **Step 2: 注册路由**

在 `backend/app/main.py` 中：

```python
from app.api import reading
app.include_router(reading.router, prefix=settings.API_PREFIX)
```

---

## Task 5: 清理脚本

**Files:**
- Create: `backend/scripts/cleanup_reading_cache.py`

- [ ] **Step 1: 创建脚本**

```python
#!/usr/bin/env python3
import sys
from pathlib import Path

# 将 backend 目录加入路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.reading_service import cleanup_reading_cache

if __name__ == "__main__":
    cleanup_reading_cache()
    print("Reading cache cleaned up")
```

- [ ] **Step 2: 测试脚本**

```bash
cd /home/yuanwu/cynthia-study/backend
source venv/bin/activate
python scripts/cleanup_reading_cache.py
```

- [ ] **Step 3: 提供 crontab 示例**

在实现完成后，向用户给出：

```cron
0 3 * * * cd /home/yuanwu/cynthia-study && /home/yuanwu/cynthia-study/backend/venv/bin/python backend/scripts/cleanup_reading_cache.py >> /home/yuanwu/cynthia-study/logs/reading_cleanup.log 2>&1
```

---

## Task 6: 前端 API 模块

**Files:**
- Create: `frontend/src/api/reading.ts`

- [ ] **Step 1: 创建 API 封装**

```typescript
import request from './index'

export interface ReadingItem {
  name: string
  path: string
  is_dir: boolean
  size?: number
}

export interface ReadingReadResult {
  task_id: string
  pages: number
  image_urls: string[]
}

export function listReadingDirectory(path?: string) {
  return request.get('/api/reading/list', { params: { path } })
}

export function readBook(path: string) {
  return request.post('/api/reading/read', { path })
}

export function cleanupReadingCache() {
  return request.post('/api/reading/cleanup')
}
```

---

## Task 7: 阅读页面

**Files:**
- Create: `frontend/src/views/Reading.vue`
- Create: `frontend/src/views/Reading.css`

- [ ] **Step 1: 创建页面结构**

包含：
- 返回首页按钮
- 页面标题：`📖 绘本阅读`
- 描述：「选择云端绘本，点击即可全屏阅读」
- 内容区：左侧 `el-tree`（目录树），右侧文件列表

- [ ] **Step 2: 实现目录加载**

```typescript
const loadTree = async (path?: string) => {
  const res = await listReadingDirectory(path) as any
  if (res.success && res.data) {
    treeData.value = res.data.map((item: ReadingItem) => ({
      label: item.name,
      path: item.path,
      isLeaf: !item.is_dir,
      data: item,
    }))
  }
}
```

- [ ] **Step 3: 实现懒加载**

Element Plus 的 `el-tree` 支持 `lazy` 和 `load` 属性。点击目录节点时调用 `loadTree(node.data.path)` 加载子目录。

- [ ] **Step 4: 文件列表点击**

点击非目录节点时，调用 `readBook(item.path)`，打开 `Reader` 组件全屏阅读。

- [ ] **Step 5: 应用样式**

遵循 `DESIGN.md`：渐变背景、白色大圆角卡片、青色主题。

---

## Task 8: 全屏阅读器组件

**Files:**
- Create: `frontend/src/components/Reader.vue`

- [ ] **Step 1: 创建组件**

Props：`imageUrls: string[]`、`title: string`
Emits：`close`

- [ ] **Step 2: 实现翻页与键盘控制**

```typescript
const currentPage = ref(0)
const nextPage = () => { if (currentPage.value < props.imageUrls.length - 1) currentPage.value++ }
const prevPage = () => { if (currentPage.value > 0) currentPage.value-- }

const onKeydown = (e: KeyboardEvent) => {
  if (e.key === 'ArrowRight') nextPage()
  if (e.key === 'ArrowLeft') prevPage()
  if (e.key === 'Escape') emit('close')
}
```

- [ ] **Step 3: 实现打印**

```typescript
const printAll = () => window.print()
```

打印样式通过 CSS `@media print` 隐藏控件、显示所有图片。

- [ ] **Step 4: 全屏样式**

```css
.reader-overlay {
  position: fixed;
  inset: 0;
  background: #000;
  z-index: 2000;
  display: flex;
  flex-direction: column;
}

.reader-image {
  max-width: 100%;
  max-height: 100vh;
  object-fit: contain;
  margin: 0 auto;
}

@media print {
  .reader-controls, .reader-overlay { background: #fff; }
  .reader-image { page-break-after: always; display: block; }
}
```

---

## Task 9: 首页与导航集成

**Files:**
- Modify: `frontend/src/views/Home.vue`
- Modify: `frontend/src/router/index.ts`
- Modify: `frontend/src/components/QuickNav.vue`

- [ ] **Step 1: 新增首页卡片**

在 `Home.vue` 的 `tools-container` 中，在「益智游戏中心」后插入：

```vue
<router-link to="/reading" class="tool-card reading">
  <span class="tool-icon">📖</span>
  <h2>绘本阅读</h2>
  <p>从云端读取绘本<br/>在线全屏阅读，支持打印</p>
  <span class="tool-arrow">→</span>
</router-link>
```

- [ ] **Step 2: 新增路由**

在 `frontend/src/router/index.ts` 中追加：

```typescript
{
  path: '/reading',
  name: 'Reading',
  component: () => import('@/views/Reading.vue')
}
```

- [ ] **Step 3: 新增 QuickNav 入口**

在 `frontend/src/components/QuickNav.vue` 中追加阅读入口：

```vue
<router-link to="/reading" class="nav-item" :class="{ active: $route.path === '/reading' }">
  <span class="nav-icon">📖</span>
</router-link>
```

- [ ] **Step 4: 新增首页卡片样式**

在 `frontend/src/views/Home.css` 中给 `.tool-card.reading` 添加 hover 边框色：`#00BCD4`（primary-teal）。

---

## Task 10: 验证与收尾

- [ ] **Step 1: 后端启动检查**

```bash
cd /home/yuanwu/cynthia-study/backend
source venv/bin/activate
python -m uvicorn app.main:app --reload
```

确认 `/docs` 下出现 `/api/reading/*` 接口。

- [ ] **Step 2: 前端启动检查**

```bash
cd /home/yuanwu/cynthia-study/frontend
npm run dev
```

确认首页出现「绘本阅读」卡片，点击进入 `/reading` 页面。

- [ ] **Step 3: 本地转换测试**

先用本地 `@read/` 文件或手动复制到 `backend/data/cache/reading/` 测试转换与图片访问。

- [ ] **Step 4: 配置百度凭证并测试**

创建 `~/.config/cynthia-study/baidu_config.json`，从 libretv-enhanced 复制凭证，测试 `/api/reading/list` 是否能列出目标目录。

- [ ] **Step 5: 测试全屏阅读与打印**

点击文件后，验证全屏展示、左右翻页、ESC 退出、打印按钮可用。

- [ ] **Step 6: 测试清理脚本**

运行清理脚本，确认 `backend/data/cache/reading/` 被清空。

- [ ] **Step 7: 更新 README（可选）**

在 README 的功能列表中新增「绘本阅读」模块。

---

## 验收标准

- [ ] 首页出现「绘本阅读」入口卡片，点击进入 `/reading`。
- [ ] `/reading` 页面显示树形目录和文件列表，遵循 `DESIGN.md` 风格。
- [ ] 点击 PDF/PPT 文件后，后端下载并转换为图片，前端全屏展示。
- [ ] 阅读器支持左右翻页、ESC 退出、打印所有图片。
- [ ] 图片按原文件比例自适应，不偏斜、不裁剪。
- [ ] 配置百度凭证后，能从 `/团团园圆/绘本/【1】3000套中文绘本（67G）` 列出文件。
- [ ] 清理脚本能删除 `backend/data/cache/reading/` 下所有文件。
- [ ] 后端没有新增 `console.log` 调试语句或 TODO；前端同理。

---

## 依赖检查清单

- [ ] 系统已安装 `libreoffice`（soffice）
- [ ] 后端已安装 `pymupdf`、`requests`、`requests-toolbelt`、`urllib3`
- [ ] 已创建 `~/.config/cynthia-study/baidu_config.json` 并填写凭证
- [ ] 已配置 crontab 每日运行清理脚本
