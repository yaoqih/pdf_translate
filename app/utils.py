import os
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional
import aiofiles
from fastapi import UploadFile
from pathlib import Path
import PyPDF2
from .models import PDFFile, FileStatus, Language
from .database import SessionLocal

UPLOAD_DIR = "uploads"
Path(UPLOAD_DIR).mkdir(exist_ok=True)

def get_pdf_page_count(file_path: str) -> Optional[int]:
    """获取PDF文件的页数"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            return len(pdf_reader.pages)
    except Exception:
        return None

def generate_key(length: int = 32) -> str:
    """生成随机密钥"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def calculate_expiry_date(days: int = 30) -> datetime:
    """计算过期时间"""
    return datetime.utcnow() + timedelta(days=days)

async def save_upload_file(file: UploadFile, directory: str = UPLOAD_DIR) -> str:
    """保存上传的文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(directory, filename)
    
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    
    return file_path

def delete_file(file_path: str) -> bool:
    """删除文件"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception:
        pass
    return False

def get_file_size(file_path: str) -> Optional[int]:
    """获取文件大小"""
    try:
        return os.path.getsize(file_path)
    except Exception:
        return None

async def translate_pdf(file_id: int, file_path: str, source_language: Language, db_session, translate_pages: Optional[int] = None) -> None:
    """
    翻译PDF文件
    这是一个示例实现，你需要替换为实际的翻译函数
    
    参数:
        file_id: PDF文件ID
        file_path: 原始PDF文件路径
        source_language: 源语言
        db_session: 数据库会话工厂
        translate_pages: 要翻译的页数，如果为None则翻译全部页面
    """
    db = SessionLocal()
    print(f"translate_pages: {translate_pages}, file_path: {file_path}, source_language: {source_language}, file_id: {file_id}")
    try:
        # 获取PDF文件总页数
        total_pages = get_pdf_page_count(file_path)
        if not total_pages:
            raise Exception("无法获取PDF页数")

        # 确定要翻译的页数
        pages_to_translate = min(translate_pages, total_pages) if translate_pages else total_pages
        
        # 更新状态为处理中
        pdf_file = db.query(PDFFile).filter(PDFFile.id == file_id).first()
        if not pdf_file:
            return
        
        pdf_file.file_status = FileStatus.PROCESSING
        pdf_file.translated_pages = pages_to_translate
        db.commit()
        
        # TODO: 在这里实现实际的PDF翻译逻辑
        # 1. 调用你的翻译函数，传入pages_to_translate参数
        # 2. 生成翻译后的PDF文件
        # 3. 保存翻译后的文件路径
        
        # 示例：生成翻译后的文件路径
        translated_filename = f"translated_{os.path.basename(file_path)}"
        translated_path = os.path.join(UPLOAD_DIR, translated_filename)
        
        # TODO: 调用实际的翻译函数
        # translate_result = your_translation_function(
        #     file_path, 
        #     translated_path, 
        #     source_language, 
        #     pages_to_translate
        # )
        
        # 更新密钥使用情况
        key_obj = pdf_file.translation_key
        key_obj.page_count -= pages_to_translate
        key_obj.used_count += 1
        key_obj.is_active = 1 if key_obj.page_count > 0 else 0
        
        # 更新文件状态
        pdf_file.file_status = FileStatus.COMPLETED
        pdf_file.translated_path = translated_path
        db.commit()
        
    except Exception as e:
        # 发生错误时更新状态
        if 'pdf_file' in locals():
            pdf_file.file_status = FileStatus.FAILED
            pdf_file.error_message = str(e)
            db.commit()
    finally:
        db.close()