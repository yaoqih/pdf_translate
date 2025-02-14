from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models import PDFFile, TranslationKey, FileStatus, OrderStatus, Language
from ..schemas import PDFFileCreate, Response
from ..utils import save_upload_file, delete_file, get_pdf_page_count, translate_pdf
import os
from datetime import datetime
import logging
from sqlalchemy import func
import asyncio

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/upload", response_model=Response)
async def upload_pdf(
    file: UploadFile = File(...),
    key: str = Form(...),
    source_language: Language = Form(Language.EN_TO_ZH),
    translate_pages: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """上传PDF文件"""
    logger.info(f"Uploading file {file.filename} with key {key}")
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="只支持PDF文件")
    
    # 验证密钥
    key_obj = db.query(TranslationKey).filter(
        TranslationKey.key == key,
        TranslationKey.is_active == 1
    ).first()
    
    if not key_obj:
        raise HTTPException(status_code=400, detail="无效的密钥")
    
    # 保存文件
    file_path = await save_upload_file(file)
    logger.info(f"File saved to {file_path}")
    
    try:
        # 获取PDF页数
        page_count = get_pdf_page_count(file_path)
        if page_count is None:
            delete_file(file_path)
            raise HTTPException(status_code=400, detail="无法读取PDF页数")
        
        logger.info(f"PDF page count: {page_count}")
        
        # 确定要翻译的页数
        pages_to_translate = min(translate_pages, page_count) if translate_pages else page_count
        
        # 检查页数是否足够
        if key_obj.page_count < pages_to_translate:
            delete_file(file_path)
            raise HTTPException(
                status_code=400, 
                detail=f"密钥可用页数不足，需要{pages_to_translate}页，但密钥只有{key_obj.page_count}页",
                headers={"X-PDF-Page-Count": str(page_count)}
            )
        
        # 创建文件记录
        pdf_file = PDFFile(
            filename=file.filename,
            original_path=file_path,
            page_count=page_count,
            file_status=FileStatus.PENDING,
            order_status=OrderStatus.UNPAID,
            source_language=source_language,
            key_id=key_obj.id
        )
        
        db.add(pdf_file)
        db.commit()
        db.refresh(pdf_file)
        
        # 异步调用翻译函数
        asyncio.create_task(translate_pdf(pdf_file.id, file_path, source_language, get_db, pages_to_translate))
        
        logger.info(f"File uploaded successfully. ID: {pdf_file.id}")
        
        # 计算已使用的总页数
        used_pages = db.query(PDFFile).filter(
            PDFFile.key_id == key_obj.id,
            PDFFile.file_status == FileStatus.COMPLETED  # 只统计翻译完成的文件
        ).with_entities(
            func.sum(PDFFile.translated_pages)
        ).scalar() or 0
        
        return {
            "code": 200,
            "message": "文件上传成功，开始翻译处理",
            "data": {
                "file_id": pdf_file.id,
                "filename": pdf_file.filename,
                "page_count": page_count,
                "translated_pages": pages_to_translate,
                "key_info": {
                    "key": key_obj.key,
                    "page_count": key_obj.page_count,
                    "used_count": used_pages,
                    "total_pages": key_obj.page_count + used_pages,
                    "max_uses": key_obj.max_uses,
                    "is_active": key_obj.is_active
                }
            }
        }
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        if file_path and os.path.exists(file_path):
            delete_file(file_path)
        raise

@router.get("/download/{file_id}", response_class=FileResponse)
def download_pdf(file_id: int, type: str = "original", db: Session = Depends(get_db)):
    """下载PDF文件"""
    pdf_file = db.query(PDFFile).filter(PDFFile.id == file_id).first()
    if not pdf_file:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    if type == "translated" and not pdf_file.translated_path:
        raise HTTPException(status_code=400, detail="翻译文件尚未生成")
    
    file_path = pdf_file.translated_path if type == "translated" else pdf_file.original_path
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        file_path,
        filename=f"{'translated_' if type == 'translated' else ''}{pdf_file.filename}",
        media_type="application/pdf"
    )

@router.get("/list", response_model=Response)
def list_pdf_files(
    page: int = 1,
    size: int = 10,
    key: Optional[str] = None,
    file_status: Optional[str] = None,
    order_status: Optional[str] = None,
    is_admin: bool = False,
    db: Session = Depends(get_db)
):
    """获取PDF文件列表"""
    query = db.query(PDFFile)
    
    # 普通用户必须提供密钥
    if not is_admin:
        if not key:
            return {
                "code": 200,
                "message": "获取成功",
                "data": {
                    "items": [],
                    "key_info": None
                },
                "total": 0,
                "page": page,
                "size": size
            }
        
        # 获取密钥信息
        key_obj = db.query(TranslationKey).filter(
            TranslationKey.key == key
        ).first()
        
        if not key_obj:
            raise HTTPException(status_code=400, detail="无效的密钥")
        
        # 计算已使用的总页数
        used_pages = db.query(PDFFile).filter(
            PDFFile.key_id == key_obj.id
        ).with_entities(
            func.sum(PDFFile.translated_pages)
        ).scalar() or 0
        
        key_info = {
            "key": key_obj.key,
            "page_count": key_obj.page_count,
            "used_count": used_pages,
            "total_pages": key_obj.page_count + used_pages,
            "max_uses": key_obj.max_uses,
            "is_active": key_obj.is_active,
            "expired_at": key_obj.expired_at
        }
        
        query = query.join(TranslationKey).filter(
            TranslationKey.key == key
        )
    else:
        # 管理端查询时，如果提供了密钥则按密钥过滤
        if key:
            query = query.join(TranslationKey).filter(
                TranslationKey.key == key
            )
        key_info = None
    
    if file_status:
        query = query.filter(PDFFile.file_status == FileStatus(file_status))
    if order_status:
        query = query.filter(PDFFile.order_status == OrderStatus(order_status))
    
    total = query.count()
    files = query.order_by(PDFFile.created_at.desc()).offset((page - 1) * size).limit(size).all()
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "items": [
                {
                    "id": f.id,
                    "filename": f.filename,
                    "page_count": f.page_count,
                    "translated_pages": f.translated_pages,
                    "file_status": f.file_status.value,
                    "order_status": f.order_status.value,
                    "created_at": f.created_at,
                    "updated_at": f.updated_at,
                    "error_message": f.error_message,
                    "source_language": f.source_language.value,
                    "has_key": bool(f.key_id)
                }
                for f in files
            ],
            "key_info": key_info,
            "total": total,
            "page": page,
            "size": size
        }
    }

@router.delete("/{file_id}", response_model=Response)
def delete_pdf(file_id: int, db: Session = Depends(get_db)):
    """删除PDF文件"""
    pdf_file = db.query(PDFFile).filter(PDFFile.id == file_id).first()
    if not pdf_file:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 删除物理文件
    if pdf_file.original_path:
        delete_file(pdf_file.original_path)
    if pdf_file.translated_path:
        delete_file(pdf_file.translated_path)
    
    # 删除数据库记录
    db.delete(pdf_file)
    db.commit()
    
    return {
        "code": 200,
        "message": "文件删除成功",
        "data": None
    } 