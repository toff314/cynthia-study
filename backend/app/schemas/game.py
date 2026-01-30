"""益智游戏Schema"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class GameContent(BaseModel):
    """游戏内容基类"""
    pass


class IdiomChainContent(GameContent):
    """成语接龙游戏内容"""
    chain: List[Dict[str, Any]] = Field(default_factory=list, description="成语链：[{word: '成语', chars: ['成','语'], blanks: [False, False, True, True]}, ...]")
    difficulty: str = Field(default="normal", description="难度：easy/normal/hard")


class WordChainContent(GameContent):
    """英语单词接龙游戏内容"""
    chain: List[Dict[str, Any]] = Field(default_factory=list, description="单词链：[{word: 'apple', letters: ['a','p','p','l','e'], blanks: [False, False, True, True, True]}, ...]")
    difficulty: str = Field(default="normal", description="难度：easy/normal/hard")


class SudokuContent(GameContent):
    """数独游戏内容"""
    grid: List[List[int]] = Field(description="数独网格，0表示空格")
    solution: List[List[int]] = Field(description="完整解答")
    size: int = Field(description="网格大小：4/6/9")
    difficulty: str = Field(default="normal", description="难度：easy/normal/hard")


class Point24Content(GameContent):
    """24点游戏内容"""
    equations: List[Dict[str, Any]] = Field(default_factory=list, description="等式列表：[{numbers: [1,2,3,4], target: 24}, ...]")
    target: int = Field(default=24, description="目标数字")
    numbers: Optional[List[int]] = Field(default=None, description="四个数字（兼容旧版）")
    solutions: Optional[List[str]] = Field(default=None, description="可能的解答示例（兼容旧版）")


class ChessContent(GameContent):
    """棋类游戏内容"""
    board_type: str = Field(description="棋盘类型：chess/checkers/go/xiangqi")
    board_size: int = Field(description="棋盘大小")
    instructions: str = Field(description="游戏说明")


class ParentChildContent(GameContent):
    """亲子类游戏内容"""
    cards: List[Dict[str, Any]] = Field(description="游戏卡片列表")
    title: str = Field(description="游戏标题")
    instructions: str = Field(description="游戏说明")


class GameBase(BaseModel):
    """游戏基础信息"""
    game_type: str = Field(..., description="游戏类型：idiom_chain/word_chain/sudoku/point24/chess/parent_child")
    age_group: str = Field(..., description="年龄段：low/mid/high")
    title: str = Field(..., description="游戏标题")
    difficulty: str = Field(default="normal", description="难度：easy/normal/hard")


class GameCreate(GameBase):
    """创建游戏请求"""
    content: Dict[str, Any] = Field(..., description="游戏内容")


class GameResponse(GameBase):
    """游戏响应"""
    id: int
    content: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GameGenerateRequest(BaseModel):
    """生成游戏请求"""
    game_type: str = Field(..., description="游戏类型")
    age_group: str = Field(..., description="年龄段：low/mid/high")
    difficulty: str = Field(default="normal", description="难度")
    count: int = Field(default=1, description="生成数量")


class GameGenerateResponse(BaseModel):
    """生成游戏响应"""
    success: bool
    data: List[GameResponse]
    message: str


class GameListResponse(BaseModel):
    """游戏列表响应"""
    success: bool
    data: dict
    message: str


class IdiomChainGenerateRequest(BaseModel):
    """成语接龙生成请求"""
    age_group: str = Field(..., description="年龄段：low/mid/high")
    difficulty: str = Field(default="normal", description="难度")
    chain_length: int = Field(default=10, description="成语链长度")
    blank_ratio: float = Field(default=0.3, description="空缺比例")


class WordChainGenerateRequest(BaseModel):
    """单词接龙生成请求"""
    age_group: str = Field(..., description="年龄段：low/mid/high")
    difficulty: str = Field(default="normal", description="难度")
    chain_length: int = Field(default=10, description="单词链长度")
    blank_ratio: float = Field(default=0.3, description="空缺比例")


class SudokuGenerateRequest(BaseModel):
    """数独生成请求"""
    size: int = Field(..., description="网格大小：4/6/9")
    difficulty: str = Field(default="normal", description="难度：easy/normal/hard")


class Point24GenerateRequest(BaseModel):
    """24点生成请求"""
    difficulty: str = Field(default="normal", description="难度")
    count: int = Field(default=1, description="生成等式的数量")


class ChessGenerateRequest(BaseModel):
    """棋类生成请求"""
    board_type: str = Field(..., description="棋盘类型")
    board_size: int = Field(default=8, description="棋盘大小")


class ParentChildGenerateRequest(BaseModel):
    """亲子类游戏生成请求"""
    game_types: List[str] = Field(..., description="游戏类型列表：['simon_says', 'who_is_undercover', 'reverse_command', ...]")
    card_count: int = Field(default=6, description="生成卡片数量：6/8/10")


class ChessPiecesGenerateRequest(BaseModel):
    """棋子生成请求"""
    chess_type: str = Field(..., description="棋类类型：go/chess/xiangqi")
    board_size: int = Field(default=19, description="棋盘大小（围棋需要）")


class ChessPiecesContent(GameContent):
    """棋子内容"""
    chess_type: str = Field(description="棋类类型")
    board_size: int = Field(description="棋盘大小")
    pieces: Dict[str, Any] = Field(description="棋子详情")
    title: str = Field(description="标题")
    total_count: int = Field(description="总数量")
