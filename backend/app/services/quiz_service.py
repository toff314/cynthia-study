"""阅读题业务逻辑服务"""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any

from app.config import settings
from app.schemas.quiz import FileInfo, QuizData
from app.utils.file_helper import generate_filename, get_file_size


class QuizService:
    """阅读题服务类"""
    
    def __init__(self):
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
        filename = generate_filename(title)
        file_path = self.quiz_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return {
            "filename": filename,
            "path": str(file_path)
        }
    
    def upload_file(self, content: str, title: str) -> Dict[str, str]:
        """上传并保存文件"""
        try:
            data = json.loads(content)
            return self.save_quiz(data)
        except json.JSONDecodeError:
            return {
                "filename": "",
                "path": ""
            }
