"""FastAPI 应用主入口"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn

from app.config import settings
from app.api import health, schedule, quiz, achievement, statistics, game, study
from app.database import init_db

# 创建 FastAPI 应用
app = FastAPI(
    title="寒假工具集 API",
    description="寒假每日任务日程表和阅读题生成器后端API",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(health.router)
app.include_router(schedule.router, prefix=settings.API_PREFIX)
app.include_router(quiz.router, prefix=settings.API_PREFIX)
app.include_router(achievement.router, prefix=settings.API_PREFIX)
app.include_router(statistics.router, prefix=settings.API_PREFIX)
app.include_router(game.router, prefix=settings.API_PREFIX)
app.include_router(study.router, prefix=settings.API_PREFIX)

# 挂载静态文件（前端）
# frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
# if frontend_dist.exists():
#     app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    init_db()
    print("Database initialized successfully")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用寒假工具集 API",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
