"""统计API"""

from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.statistics_service import StatisticsService
from app.schemas.statistics import StatisticsSummary, StatisticsResponse

router = APIRouter()


@router.get("/statistics/summary", response_model=StatisticsResponse)
async def get_statistics_summary(db: Session = Depends(get_db)):
    """
    获取统计摘要信息
    
    返回:
        StatisticsResponse: 包含总用户数、总访问次数和最后更新时间
    """
    try:
        statistics_service = StatisticsService(db)
        summary = statistics_service.get_summary()
        
        return StatisticsResponse(
            success=True,
            data=summary
        )
    except Exception as e:
        return StatisticsResponse(
            success=False,
            message=f"获取统计数据失败: {str(e)}"
        )


@router.post("/statistics/record")
async def record_visit(request: Request, db: Session = Depends(get_db)):
    """
    记录页面访问
    
    从请求对象中获取IP地址和用户代理信息，记录用户访问
    """
    try:
        statistics_service = StatisticsService(db)
        
        # 从请求对象获取IP地址
        ip_address = statistics_service.get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "")
        
        # 构建记录请求
        from app.schemas.statistics import RecordVisitRequest
        record_request = RecordVisitRequest(
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # 记录访问
        success = statistics_service.record_visit(record_request)
        
        if success:
            return {"success": True, "message": "访问记录成功"}
        else:
            return {"success": False, "message": "访问记录失败"}
    except Exception as e:
        return {"success": False, "message": f"记录访问异常: {str(e)}"}
