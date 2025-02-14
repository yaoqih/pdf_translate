from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models import PDFFile, FileStatus, OrderStatus
from ..schemas import Response
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.put("/file/{file_id}", response_model=Response)
def update_file_status(
    file_id: int,
    status: FileStatus,
    error_message: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """更新文件处理状态"""
    pdf_file = db.query(PDFFile).filter(PDFFile.id == file_id).first()
    if not pdf_file:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    pdf_file.file_status = status
    if error_message:
        pdf_file.error_message = error_message
    
    db.commit()
    db.refresh(pdf_file)
    
    return {
        "code": 200,
        "message": "状态更新成功",
        "data": {
            "id": pdf_file.id,
            "status": pdf_file.file_status.value,
            "error_message": pdf_file.error_message
        }
    }

@router.put("/order/{file_id}", response_model=Response)
def update_order_status(
    file_id: int,
    status: OrderStatus,
    db: Session = Depends(get_db)
):
    """更新订单状态"""
    pdf_file = db.query(PDFFile).filter(PDFFile.id == file_id).first()
    if not pdf_file:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    pdf_file.order_status = status
    db.commit()
    db.refresh(pdf_file)
    
    return {
        "code": 200,
        "message": "状态更新成功",
        "data": {
            "id": pdf_file.id,
            "status": pdf_file.order_status.value
        }
    }

@router.get("/statistics", response_model=Response)
def get_statistics(db: Session = Depends(get_db)):
    """获取状态统计信息"""
    logger.info("Getting statistics")
    try:
        # 文件状态统计
        file_stats = {status.value: 0 for status in FileStatus}
        for status in FileStatus:
            count = db.query(PDFFile).filter(PDFFile.file_status == status).count()
            file_stats[status.value] = count
        
        # 订单状态统计
        order_stats = {status.value: 0 for status in OrderStatus}
        for status in OrderStatus:
            count = db.query(PDFFile).filter(PDFFile.order_status == status).count()
            order_stats[status.value] = count
        
        logger.info(f"Statistics: file_stats={file_stats}, order_stats={order_stats}")
        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "file_status": file_stats,
                "order_status": order_stats
            }
        }
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="获取统计信息失败") 