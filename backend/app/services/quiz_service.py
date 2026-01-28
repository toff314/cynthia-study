"""阅读题业务逻辑服务"""

import hashlib
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.config import settings
from app.models.file_metadata import FileMetadata
from app.schemas.quiz import FileInfo, QuizData
from app.utils.file_helper import (
    generate_filename,
    get_file_size,
    validate_filename,
    validate_content_size,
    MAX_FILE_SIZE
)


class QuizService:
    """阅读题服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.quiz_dir = settings.QUIZ_DIR
    
    def get_files(self) -> List[FileInfo]:
        """获取JSON文件列表"""
        files = []
        for file_path in self.quiz_dir.glob("*.json"):
            stat = file_path.stat()
            modified = stat.st_mtime
            # 格式化修改时间
            from datetime import datetime
            modified_str = datetime.fromtimestamp(modified).strftime("%Y-%m-%dT%H:%M:%S")
            
            files.append(FileInfo(
                name=file_path.name,
                size=get_file_size(file_path),
                modified=modified_str
            ))
        
        # 按修改时间降序排序
        files.sort(key=lambda x: x.modified, reverse=True)
        return files
    
    def get_file_content(self, filename: str) -> Optional[str]:
        """获取文件内容"""
        file_path = self.quiz_dir / filename
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None
    
    def save_quiz(self, data: Dict[str, Any]) -> Dict[str, str]:
        """保存阅读题数据到文件"""
        title = data.get("title", "quiz")
        
        # 转换为JSON字符串以计算MD5
        json_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        md5_hash = self._calculate_md5(json_str)
        
        # 检查是否已存在相同MD5的文件
        existing = self.db.query(FileMetadata).filter(
            FileMetadata.md5_hash == md5_hash,
            FileMetadata.file_type == "quiz"
        ).first()
        
        if existing:
            # 返回已存在的文件名，提示用户文件已存在
            return {
                "filename": existing.filename,
                "path": str(self.quiz_dir / existing.filename),
                "message": f"文件已存在（MD5相同）: {existing.filename}",
                "skipped": True
            }
        
        filename = generate_filename(title)
        
        # 验证生成的文件名是否安全
        is_valid, error_msg = validate_filename(filename)
        if not is_valid:
            raise ValueError(f"文件名验证失败: {error_msg}")
        
        file_path = self.quiz_dir / filename
        
        # 验证文件路径是否在允许的目录内（防止路径遍历）
        try:
            file_path.resolve().relative_to(self.quiz_dir.resolve())
        except ValueError:
            raise ValueError("文件路径不在允许的目录内")
        
        # 保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 记录文件元数据
        file_size = file_path.stat().st_size
        metadata = FileMetadata(
            filename=filename,
            md5_hash=md5_hash,
            file_type="quiz",
            file_size=file_size
        )
        self.db.add(metadata)
        self.db.commit()
        
        return {
            "filename": filename,
            "path": str(file_path),
            "message": "文件保存成功",
            "skipped": False
        }
    
    def upload_file(self, content: str, title: str) -> Dict[str, str]:
        """上传并保存文件"""
        # 验证内容大小是否超过限制
        is_valid, error_msg = validate_content_size(content, MAX_FILE_SIZE)
        if not is_valid:
            raise ValueError(error_msg)
        
        # 检查内容是否包含危险的JSON模式（防止JSON注入）
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON格式错误: {str(e)}")
        
        # 验证JSON数据结构的基本安全性
        if not isinstance(data, dict):
            raise ValueError("JSON数据必须是对象类型")
        
        # 检查数据中是否包含潜在的恶意内容
        self._validate_json_safety(data)
        
        return self.save_quiz(data)
    
    def _calculate_md5(self, content: str) -> str:
        """计算内容的MD5哈希值"""
        md5 = hashlib.md5()
        md5.update(content.encode('utf-8'))
        return md5.hexdigest()
    
    def _validate_json_safety(self, data: Dict[str, Any], depth: int = 0) -> None:
        """
        验证JSON数据的安全性
        
        参数:
            data: 待验证的数据
            depth: 当前递归深度，防止过深嵌套
        """
        # 防止过深嵌套（可能导致栈溢出）
        MAX_DEPTH = 20
        if depth > MAX_DEPTH:
            raise ValueError(f"JSON数据嵌套层级过深（最大{MAX_DEPTH}层）")
        
        # 限制数组长度
        MAX_ARRAY_LENGTH = 1000
        if isinstance(data, list):
            if len(data) > MAX_ARRAY_LENGTH:
                raise ValueError(f"数组长度超出限制（最大{MAX_ARRAY_LENGTH}元素）")
            for item in data:
                self._validate_json_safety(item, depth + 1)
        
        # 检查字符串内容（防止XSS等攻击）
        elif isinstance(data, str):
            # 限制单个字符串长度
            MAX_STRING_LENGTH = 10000
            if len(data) > MAX_STRING_LENGTH:
                raise ValueError(f"字符串长度超出限制（最大{MAX_STRING_LENGTH}字符）")
            
            # 检查潜在的脚本注入标签
            dangerous_patterns = ['<script', '</script', 'javascript:', 'eval(', 'setTimeout(', 'setInterval(']
            data_lower = data.lower()
            for pattern in dangerous_patterns:
                if pattern in data_lower:
                    raise ValueError(f"JSON内容包含潜在危险: {pattern}")
        
        # 递归检查字典
        elif isinstance(data, dict):
            # 限制字典键数量
            MAX_DICT_KEYS = 100
            if len(data) > MAX_DICT_KEYS:
                raise ValueError(f"字典键数量超出限制（最大{MAX_DICT_KEYS}）")
            
            for key, value in data.items():
                # 检查键名
                if not isinstance(key, str):
                    raise ValueError("字典键必须是字符串类型")
                if len(key) > 200:
                    raise ValueError(f"字典键名过长（最大200字符）: {key[:50]}...")
                
                self._validate_json_safety(value, depth + 1)
