from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base

class FileStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class OrderStatus(enum.Enum):
    UNPAID = "unpaid"
    PAID = "paid"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class Language(enum.Enum):
    EN_TO_ZH = "en_to_zh"
    ZH_TO_EN = "zh_to_en"
    JA_TO_ZH = "ja_to_zh"
    KO_TO_ZH = "ko_to_zh"
    FR_TO_ZH = "fr_to_zh"
    DE_TO_ZH = "de_to_zh"
    ES_TO_ZH = "es_to_zh"
    RU_TO_ZH = "ru_to_zh"

class TranslationKey(Base):
    __tablename__ = "translation_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(64), unique=True, index=True)
    page_count = Column(Integer)
    used_count = Column(Integer, default=0)
    max_uses = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    expired_at = Column(DateTime)
    is_active = Column(Integer, default=1)
    
    # 关联关系
    pdf_files = relationship("PDFFile", back_populates="translation_key")

class PDFFile(Base):
    __tablename__ = "pdf_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255))
    original_path = Column(String(255))
    translated_path = Column(String(255), nullable=True)
    page_count = Column(Integer)
    translated_pages = Column(Integer, nullable=True)
    file_status = Column(Enum(FileStatus), default=FileStatus.PENDING)
    order_status = Column(Enum(OrderStatus), default=OrderStatus.UNPAID)
    key_id = Column(Integer, ForeignKey("translation_keys.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    error_message = Column(Text, nullable=True)
    source_language = Column(Enum(Language), default=Language.EN_TO_ZH)
    
    # 关联关系
    translation_key = relationship("TranslationKey", back_populates="pdf_files") 