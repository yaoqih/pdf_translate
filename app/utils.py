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
import asyncio
from pdf2zh import translate as pdf_translate
import os
from dotenv import load_dotenv

load_dotenv()

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
    使用pdf2zh和OpenAI服务进行翻译
    
    参数:
        file_id: PDF文件ID
        file_path: 原始PDF文件路径
        source_language: 源语言
        db_session: 数据库会话工厂
        translate_pages: 要翻译的页数，如果为None则翻译全部页面
    """
    db = SessionLocal()
    print(f"translate_pages: {translate_pages}, file_path: {file_path}, source_language: {source_language}, file_id: {file_id}")
    
    # 保存原始环境变量
    original_env = {
        'OPENAI_BASE_URL': os.environ.get('OPENAI_BASE_URL'),
        'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY'),
        'OPENAI_MODEL': os.environ.get('OPENAI_MODEL')
    }
    try:
        # 设置临时环境变量
        os.environ["OPENAI_BASE_URL"] = os.getenv("OPENAI_BASE_URL", "https://api.lingyiwanwu.com/v1")
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "9b74841dc6f9441ca3e09e700168512e")
        os.environ["OPENAI_MODEL"] = os.getenv("OPENAI_MODEL", "yi-lightning")
        
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
        
        # 更新密钥使用情况（提前更新，避免重复使用）
        key_obj = pdf_file.translation_key
        if key_obj.page_count < pages_to_translate:
            raise Exception(f"密钥可用页数不足，需要{pages_to_translate}页，但密钥只剩{key_obj.page_count}页")
        
        key_obj.page_count -= pages_to_translate
        key_obj.used_count += 1
        key_obj.is_active = 1 if key_obj.page_count > 0 else 0
        
        pdf_file.file_status = FileStatus.PROCESSING
        pdf_file.translated_pages = pages_to_translate
        db.commit()

        # 准备翻译参数
        pages_list = list(range(0, pages_to_translate)) if pages_to_translate else None
        lang_map = {
            Language.EN_TO_ZH: ("en", "zh"),
            Language.ZH_TO_EN: ("zh", "en"),
        }
        lang_in, lang_out = lang_map.get(source_language, ("en", "zh"))
        
        # 设置输出目录
        output_dir = Path(UPLOAD_DIR) / str(file_id)
        output_dir.mkdir(exist_ok=True)
        
        # 调用pdf2zh进行翻译
        result_files = pdf_translate(
            files=[file_path],
            output=str(output_dir),
            pages=pages_list,
            lang_in=lang_in,
            lang_out=lang_out,
            service="openai",
            thread=4,
            envs={
                "OPENAI_API_KEY": os.environ['OPENAI_API_KEY'],
                "OPENAI_BASE_URL": os.environ['OPENAI_BASE_URL'],
                "OPENAI_MODEL": os.environ['OPENAI_MODEL']
            }
        )
        
        if not result_files:
            raise Exception("翻译失败，未生成输出文件")
            
        # 获取翻译后的文件路径（双语版本）
        _, translated_path = result_files[0]
        
        # 更新文件状态
        pdf_file.file_status = FileStatus.COMPLETED
        pdf_file.translated_path = translated_path
        db.commit()
        
    except Exception as e:
        # 发生错误时更新状态
        if 'pdf_file' in locals():
            # 如果是在更新密钥使用情况之后发生错误，需要恢复密钥的使用量
            if 'key_obj' in locals() and pdf_file.file_status == FileStatus.PROCESSING:
                key_obj.page_count += pages_to_translate
                key_obj.used_count -= 1
                key_obj.is_active = 1
            
            pdf_file.file_status = FileStatus.FAILED
            pdf_file.error_message = str(e)
            db.commit()
    finally:
        # 恢复原始环境变量
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        db.close()