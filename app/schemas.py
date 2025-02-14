from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum

class FileStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class OrderStatus(str, Enum):
    UNPAID = "unpaid"
    PAID = "paid"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class Language(str, Enum):
    EN_TO_ZH = "en_to_zh"
    ZH_TO_EN = "zh_to_en"
    JA_TO_ZH = "ja_to_zh"
    KO_TO_ZH = "ko_to_zh"
    FR_TO_ZH = "fr_to_zh"
    DE_TO_ZH = "de_to_zh"
    ES_TO_ZH = "es_to_zh"
    RU_TO_ZH = "ru_to_zh"

    @classmethod
    def get_display_name(cls, value):
        display_names = {
            "en_to_zh": "英语 → 中文",
            "zh_to_en": "中文 → 英语",
            "ja_to_zh": "日语 → 中文",
            "ko_to_zh": "韩语 → 中文",
            "fr_to_zh": "法语 → 中文",
            "de_to_zh": "德语 → 中文",
            "es_to_zh": "西班牙语 → 中文",
            "ru_to_zh": "俄语 → 中文"
        }
        return display_names.get(value, value)

# TranslationKey schemas
class TranslationKeyBase(BaseModel):
    page_count: int
    max_uses: Optional[int] = 1
    expired_at: Optional[datetime] = None

class TranslationKeyCreate(TranslationKeyBase):
    pass

class TranslationKeyMerge(BaseModel):
    target_key: str
    source_keys: List[str]

class TranslationKey(TranslationKeyBase):
    id: int
    key: str
    used_count: int
    created_at: datetime
    is_active: int

    class Config:
        from_attributes = True

# PDFFile schemas
class PDFFileBase(BaseModel):
    filename: str
    page_count: int

class PDFFileCreate(PDFFileBase):
    key: str
    source_language: Language = Language.EN_TO_ZH

class PDFFile(PDFFileBase):
    id: int
    original_path: str
    translated_path: Optional[str]
    file_status: FileStatus
    order_status: OrderStatus
    key_id: int
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str]
    source_language: Language

    class Config:
        from_attributes = True

# Response schemas
class Response(BaseModel):
    code: int
    message: str
    data: Optional[dict] = None

class PaginatedResponse(Response):
    data: dict
    total: int
    page: int
    size: int 