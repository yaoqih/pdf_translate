from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from ..database import get_db
from ..models import PDFFile, FileStatus, OrderStatus, SystemConfig
from ..schemas import Response
import logging
import os

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

@router.get("/config", response_model=Response)
def get_system_configs(db: Session = Depends(get_db)):
    """获取系统配置"""
    configs = db.query(SystemConfig).all()
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "configs": [
                {
                    "key": config.key,
                    "value": config.value,
                    "description": config.description
                }
                for config in configs
            ]
        }
    }

@router.post("/config", response_model=Response)
def update_system_configs(configs: Dict[str, str], db: Session = Depends(get_db)):
    """更新系统配置"""
    for key, value in configs.items():
        config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
        if config:
            config.value = value
        else:
            descriptions = {
                "OPENAI_BASE_URL": "OpenAI API基础URL",
                "OPENAI_API_KEY": "OpenAI API密钥",
                "OPENAI_MODEL": "OpenAI模型名称"
            }
            config = SystemConfig(
                key=key,
                value=value,
                description=descriptions.get(key, "")
            )
            db.add(config)
    
    db.commit()
    
    # 更新环境变量
    for key, value in configs.items():
        if value:
            os.environ[key] = value
        else:
            os.environ.pop(key, None)
    
    return {
        "code": 200,
        "message": "更新成功",
        "data": None
    }

@router.get("/config/init", response_model=Response)
def init_system_configs(db: Session = Depends(get_db)):
    """初始化系统配置"""
    default_configs = {
        "OPENAI_BASE_URL": {
            "value": "https://api.openai.com/v1",
            "description": "OpenAI API基础URL"
        },
        "OPENAI_API_KEY": {
            "value": "",
            "description": "OpenAI API密钥"
        },
        "OPENAI_MODEL": {
            "value": "gpt-3.5-turbo",
            "description": "OpenAI模型名称"
        }
    }
    
    for key, config in default_configs.items():
        if not db.query(SystemConfig).filter(SystemConfig.key == key).first():
            db.add(SystemConfig(
                key=key,
                value=config["value"],
                description=config["description"]
            ))
    
    db.commit()
    
    return {
        "code": 200,
        "message": "初始化成功",
        "data": None
    } 