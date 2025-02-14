from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import TranslationKey
from ..schemas import TranslationKeyCreate, TranslationKey as TranslationKeySchema, Response, TranslationKeyMerge
from ..utils import generate_key, calculate_expiry_date
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/generate", response_model=Response)
def generate_translation_key(key_data: TranslationKeyCreate, db: Session = Depends(get_db)):
    """生成新的翻译密钥"""
    logger.info(f"Generating new key with data: {key_data}")
    try:
        new_key = TranslationKey(
            key=generate_key(),
            page_count=key_data.page_count,
            max_uses=key_data.max_uses or 1,
            expired_at=key_data.expired_at or calculate_expiry_date()
        )
        db.add(new_key)
        db.commit()
        db.refresh(new_key)
        
        logger.info(f"Key generated successfully: {new_key.key}")
        return {
            "code": 200,
            "message": "密钥生成成功",
            "data": {"key": new_key.key}
        }
    except Exception as e:
        logger.error(f"Error generating key: {str(e)}")
        raise HTTPException(status_code=500, detail="生成密钥失败")

@router.get("/info/{key}", response_model=Response)
def get_key_info(key: str, db: Session = Depends(get_db)):
    """获取密钥信息"""
    key_info = db.query(TranslationKey).filter(TranslationKey.key == key).first()
    if not key_info:
        raise HTTPException(status_code=404, detail="密钥不存在")
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "key": key_info.key,
            "page_count": key_info.page_count,
            "used_count": key_info.used_count,
            "max_uses": key_info.max_uses,
            "is_active": key_info.is_active,
            "expired_at": key_info.expired_at
        }
    }

@router.post("/merge", response_model=Response)
def merge_keys(merge_data: TranslationKeyMerge, db: Session = Depends(get_db)):
    """合并多个密钥到目标密钥"""
    # 验证目标密钥
    target_key = db.query(TranslationKey).filter(
        TranslationKey.key == merge_data.target_key,
        TranslationKey.is_active == 1
    ).first()
    if not target_key:
        raise HTTPException(status_code=400, detail="目标密钥不存在或已失效")
    
    # 验证源密钥
    source_keys = db.query(TranslationKey).filter(
        TranslationKey.key.in_(merge_data.source_keys),
        TranslationKey.is_active == 1,
        TranslationKey.key != merge_data.target_key  # 排除目标密钥
    ).all()
    
    if len(source_keys) != len(merge_data.source_keys):
        raise HTTPException(status_code=400, detail="部分源密钥不存在或已失效")
    
    # 计算总页数
    total_pages = sum(key.page_count for key in source_keys)
    
    # 更新目标密钥
    target_key.page_count += total_pages
    
    # 停用源密钥
    for key in source_keys:
        key.is_active = 0
    
    db.commit()
    
    return {
        "code": 200,
        "message": "密钥合并成功",
        "data": {
            "target_key": target_key.key,
            "total_pages": target_key.page_count
        }
    }

@router.get("/list", response_model=Response)
def list_keys(
    page: int = 1,
    size: int = 10,
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    """获取密钥列表（仅管理端使用）"""
    logger.info(f"Listing keys with page={page}, size={size}, is_active={is_active}")
    try:
        query = db.query(TranslationKey)
        if is_active is not None:
            query = query.filter(TranslationKey.is_active == int(is_active))
        
        total = query.count()
        keys = query.order_by(TranslationKey.created_at.desc()).offset((page - 1) * size).limit(size).all()
        
        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "items": [
                    {
                        "key": key.key,
                        "page_count": key.page_count,
                        "used_count": key.used_count,
                        "max_uses": key.max_uses,
                        "is_active": key.is_active,
                        "created_at": key.created_at,
                        "expired_at": key.expired_at
                    }
                    for key in keys
                ],
                "total": total,
                "page": page,
                "size": size
            }
        }
    except Exception as e:
        logger.error(f"Error listing keys: {str(e)}")
        raise HTTPException(status_code=500, detail="获取密钥列表失败") 