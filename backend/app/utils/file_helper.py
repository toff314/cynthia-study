"""文件辅助函数"""

import random
import re
import string
from datetime import datetime
from pathlib import Path

from app.config import settings


def generate_random_string(length: int = 6) -> str:
    """生成随机字符串"""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def generate_filename(title: str) -> str:
    """生成文件名：标题 + 日期 + 随机值"""
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    random_str = generate_random_string(settings.FILENAME_RANDOM_LENGTH)
    
    # 清理标题中的特殊字符
    clean_title = title.replace('<', '_')\
                      .replace('>', '_')\
                      .replace(':', '_')\
                      .replace('/', '_')\
                      .replace('\\', '_')\
                      .replace('|', '_')\
                      .replace('?', '_')\
                      .replace('*', '_')
    
    return f"{clean_title}_{date_str}_{random_str}.json"


def get_file_size(file_path: Path) -> int:
    """获取文件大小"""
    return file_path.stat().st_size


def format_file_size(size: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"


MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB 文件大小限制


def validate_filename(filename: str) -> tuple[bool, str]:
    """
    验证文件名安全性，防止路径遍历和注入攻击
    
    参数:
        filename: 待验证的文件名
        
    返回:
        tuple[是否安全, 错误信息]
    """
    # 检查空文件名
    if not filename or not filename.strip():
        return False, "文件名不能为空"
    
    # 检查文件名长度
    if len(filename) > 255:
        return False, "文件名过长（最大255字符）"
    
    # 检查路径遍历攻击 (../, ..\\)
    if ".." in filename:
        return False, "文件名包含非法路径字符"
    
    # 检查绝对路径风险
    if filename.startswith("/") or filename.startswith("\\"):
        return False, "文件名不能以路径分隔符开头"
    
    # 检查Windows保留设备名
    reserved_names = [
        "CON", "PRN", "AUX", "NUL",
        "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
    ]
    filename_upper = filename.split('.')[0].upper()
    if filename_upper in reserved_names:
        return False, f"文件名使用了保留设备名: {filename_upper}"
    
    # 检查文件扩展名（只能为.json）
    if not filename.lower().endswith('.json'):
        return False, "只允许上传JSON文件"
    
    # 检查危险字符（使用正则表达式）
    # 允许中文、字母、数字、下划线、短横线、括号、书名号、空格
    dangerous_pattern = r'[<>:"|?*\x00-\x1f]'
    if re.search(dangerous_pattern, filename):
        return False, "文件名包含非法字符"
    
    # 检查控制字符
    if any(ord(c) < 32 and c not in ['\t', '\n', '\r'] for c in filename):
        return False, "文件名包含控制字符"
    
    return True, ""


def validate_content_size(content: str, max_size: int = MAX_FILE_SIZE) -> tuple[bool, str]:
    """
    验证内容大小是否超过限制
    
    参数:
        content: 待验证的内容
        max_size: 最大允许大小（字节），默认1MB
        
    返回:
        tuple[是否通过, 错误信息]
    """
    content_bytes = content.encode('utf-8')
    content_size = len(content_bytes)
    
    if content_size > max_size:
        size_str = format_file_size(content_size)
        max_str = format_file_size(max_size)
        return False, f"文件大小超出限制（{size_str} > {max_str}）"
    
    return True, ""


def validate_text_input(text: str, field_name: str, max_length: int = 200) -> tuple[bool, str]:
    """
    验证文本输入的安全性，防止XSS攻击和注入
    
    参数:
        text: 待验证的文本
        field_name: 字段名称（用于错误提示）
        max_length: 最大允许长度，默认200字符
        
    返回:
        tuple[是否安全, 错误信息]
    """
    # 检查空值或空字符串
    if not text or not text.strip():
        return True, ""  # 允许空值（由业务逻辑判断是否必填）
    
    text = text.strip()
    
    # 检查长度
    if len(text) > max_length:
        return False, f"{field_name}长度超出限制（最大{max_length}字符）"
    
    # 检查危险的HTML/XML标签（防止XSS攻击）
    xss_patterns = [
        '<script',           # script标签
        '</script',          # 闭合script标签
        '<iframe',           # iframe标签
        '<embed',            # embed标签
        '<object',           # object标签
        'javascript:',       # javascript:伪协议
        'vbscript:',         # vbscript:伪协议
        'onload=',           # onload事件
        'onerror=',          # onerror事件
        'onclick=',          # onclick事件
        'onmouseover=',      # onmouseover事件
        'onsubmit=',         # onsubmit事件
        'eval(',             # eval函数
        'setTimeout(',       # setTimeout函数
        'setInterval(',      # setInterval函数
        'document.cookie',   # cookie访问
        'document.write',    # document.write
        'innerHTML',         # innerHTML赋值
        'outerHTML',         # outerHTML赋值
        'data:text/html',    # data URL
        'expression(',       # CSS expression（IE专用）
        'fromCharCode',      # fromCharCode函数
        'String.fromCharCode'  # String.fromCharCode函数
    ]
    
    text_lower = text.lower()
    for pattern in xss_patterns:
        if pattern in text_lower:
            return False, f"{field_name}包含危险内容: {pattern}"
    
    # 检查潜在的SQL注入模式
    sql_injection_patterns = [
        "'--",               # SQL注释
        "/*",                # 多行注释开始
        "*/",                # 多行注释结束
        " or ",              # OR运算符
        " and ",             # AND运算符
        ";",                 # SQL语句分隔符
        "select *",          # SELECT语句
        "delete from",       # DELETE语句
        "insert into",       # INSERT语句
        "update ",           # UPDATE语句
        "drop table",        # DROP语句
        "union select",      # UNION注入
        "exec(",             # exec函数
        "xp_",               # SQL Server扩展存储过程
        "waitfor delay",     # 时间延迟注入
        "benchmark(",        # MySQL基准函数
        "sleep(",            # MySQL睡眠函数
        "char(",             # char函数
        "concat(",           # concat函数
        "1=1",               # 恒真条件
        "1 = 1",             # 恒真条件（带空格）
        "%27",               # 单引号URL编码
        "%22",               # 双引号URL编码
        "%3Cscript%3E"       # HTML标签URL编码
    ]
    
    text_lower = text.lower()
    for pattern in sql_injection_patterns:
        if pattern in text_lower:
            return False, f"{field_name}包含潜在注入风险: {pattern}"
    
    # 检查控制字符（除了换行、制表符等常见字符）
    dangerous_control_chars = [
        '\x00', '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07',
        '\x08', '\x0b', '\x0c', '\x0e', '\x0f', '\x10', '\x11', '\x12',
        '\x13', '\x14', '\x15', '\x16', '\x17', '\x18', '\x19', '\x1a',
        '\x1b', '\x1c', '\x1d', '\x1e', '\x1f'
    ]
    
    for char in dangerous_control_chars:
        if char in text:
            return False, f"{field_name}包含非法控制字符"
    
    return True, ""


def sanitize_text(text: str) -> str:
    """
    清理文本，移除潜在的危险字符（可选使用）
    
    参数:
        text: 待清理的文本
        
    返回:
        清理后的文本
    """
    if not text:
        return text
    
    # 移除前后空格
    text = text.strip()
    
    # 注意：这里只是简单的清理，实际应用中建议在前端也做好验证
    # 更安全的做法是验证而不是清理
    
    return text
