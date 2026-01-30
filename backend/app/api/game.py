"""益智游戏API路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.game_service import GameService
from ..schemas.game import (
    GameCreate,
    GameResponse,
    GameGenerateRequest,
    GameGenerateResponse,
    IdiomChainGenerateRequest,
    WordChainGenerateRequest,
    SudokuGenerateRequest,
    Point24GenerateRequest,
    ChessGenerateRequest,
    ParentChildGenerateRequest,
    ChessPiecesGenerateRequest
)

router = APIRouter(prefix="/games", tags=["games"])


@router.get("/categories", response_model=dict)
async def get_game_categories():
    """
    获取所有游戏分类
    
    返回按年龄段和类型分类的游戏列表
    """
    categories = GameService.get_all_game_categories()
    return {
        "success": True,
        "data": {
            "categories": categories
        },
        "message": "获取游戏分类成功"
    }


@router.get("/age-group/{age_group}", response_model=dict)
async def get_games_by_age_group(age_group: str):
    """
    根据年龄段获取游戏类型
    
    参数:
        age_group: 年龄段 (low/mid/high)
    """
    result = GameService.get_game_types_by_age_group(age_group)
    return {
        "success": True,
        "data": result,
        "message": "获取游戏类型成功"
    }


@router.get("/chess-types", response_model=dict)
async def get_chess_types():
    """
    获取棋类游戏类型列表
    """
    chess_types = GameService.get_chess_types()
    return {
        "success": True,
        "data": {
            "chess_types": chess_types
        },
        "message": "获取棋类类型成功"
    }


@router.get("/parent-child-types", response_model=dict)
async def get_parent_child_types():
    """
    获取亲子类游戏类型列表
    """
    game_types = GameService.get_parent_child_game_types()
    return {
        "success": True,
        "data": {
            "game_types": game_types
        },
        "message": "获取亲子游戏类型成功"
    }


@router.post("/generate/idiom-chain", response_model=dict)
async def generate_idiom_chain(request: IdiomChainGenerateRequest):
    """
    生成成语接龙游戏
    
    参数:
        age_group: 年龄段 (low/mid/high)
        difficulty: 难度 (easy/normal/hard)
        chain_length: 成语链长度
        blank_ratio: 空缺比例 (0-1)
    """
    content = GameService.generate_idiom_chain(
        age_group=request.age_group,
        difficulty=request.difficulty,
        chain_length=request.chain_length,
        blank_ratio=request.blank_ratio
    )
    
    return {
        "success": True,
        "data": content,
        "message": "成语接龙生成成功"
    }


@router.post("/generate/word-chain", response_model=dict)
async def generate_word_chain(request: WordChainGenerateRequest):
    """
    生成英语单词接龙游戏
    
    参数:
        age_group: 年龄段 (low/mid/high)
        difficulty: 难度 (easy/normal/hard)
        chain_length: 单词链长度
        blank_ratio: 空缺比例 (0-1)
    """
    content = GameService.generate_word_chain(
        age_group=request.age_group,
        difficulty=request.difficulty,
        chain_length=request.chain_length,
        blank_ratio=request.blank_ratio
    )
    
    return {
        "success": True,
        "data": content,
        "message": "单词接龙生成成功"
    }


@router.post("/generate/sudoku", response_model=dict)
async def generate_sudoku(request: SudokuGenerateRequest):
    """
    生成数独游戏
    
    参数:
        size: 网格大小 (4/6/9)
        difficulty: 难度 (easy/normal/hard)
    """
    content = GameService.generate_sudoku(
        size=request.size,
        difficulty=request.difficulty
    )
    
    return {
        "success": True,
        "data": content,
        "message": "数独生成成功"
    }


@router.post("/generate/point24", response_model=dict)
async def generate_point24(request: Point24GenerateRequest):
    """
    生成24点游戏
    
    参数:
        difficulty: 难度 (easy/normal/hard)
    """
    content = GameService.generate_point24(difficulty=request.difficulty)
    
    return {
        "success": True,
        "data": content,
        "message": "24点生成成功"
    }


@router.post("/generate/chess", response_model=dict)
async def generate_chess(request: ChessGenerateRequest):
    """
    生成棋类游戏
    
    参数:
        board_type: 棋盘类型 (chess/checkers/xiangqi/go)
        board_size: 棋盘大小
    """
    content = GameService.generate_chess(
        board_type=request.board_type,
        board_size=request.board_size
    )
    
    return {
        "success": True,
        "data": content,
        "message": f"{content['title']}生成成功"
    }


@router.post("/generate/parent-child", response_model=dict)
async def generate_parent_child_games(request: ParentChildGenerateRequest):
    """
    生成亲子类游戏
    
    参数:
        game_types: 游戏类型列表
    """
    content = GameService.generate_parent_child_games(request.game_types)
    
    return {
        "success": True,
        "data": content,
        "message": "亲子游戏生成成功"
    }


@router.post("/generate/chess-pieces", response_model=dict)
async def generate_chess_pieces(request: ChessPiecesGenerateRequest):
    """
    生成棋子
    
    参数:
        chess_type: 棋类类型 (go/chess/xiangqi)
        board_size: 棋盘大小（围棋需要）
    """
    content = GameService.generate_chess_pieces(
        chess_type=request.chess_type,
        board_size=request.board_size
    )
    
    return {
        "success": True,
        "data": content,
        "message": f"{content['title']}生成成功"
    }


@router.post("/save", response_model=dict)
async def save_game(game_data: GameCreate, db: Session = Depends(get_db)):
    """
    保存游戏记录到数据库
    
    参数:
        game_data: 游戏数据
    """
    try:
        game = GameService.create_game(db, game_data.dict())
        return {
            "success": True,
            "data": GameResponse.model_validate(game),
            "message": "游戏保存成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")


@router.get("/list/{game_type}", response_model=dict)
async def get_games(game_type: str, age_group: str = None, db: Session = Depends(get_db)):
    """
    获取游戏列表
    
    参数:
        game_type: 游戏类型
        age_group: 年龄段 (可选)
    """
    games = GameService.get_games_by_type(db, game_type, age_group)
    return {
        "success": True,
        "data": {
            "games": [GameResponse.model_validate(g) for g in games],
            "total": len(games)
        },
        "message": "获取游戏列表成功"
    }
