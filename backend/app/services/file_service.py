from sqlalchemy.orm import Session
from app.models import FileUpload
from app.utils import allowed_file, get_file_extension
from app.config import settings
from app.logger import logger
import os
from typing import Optional

class FileService:
    UPLOAD_DIR = "uploads"
    
    @staticmethod
    def ensure_upload_dir():
        if not os.path.exists(FileService.UPLOAD_DIR):
            os.makedirs(FileService.UPLOAD_DIR)
    
    @staticmethod
    async def save_file(db: Session, user_id: str, file_name: str, file_content: bytes) -> Optional[FileUpload]:
        if not allowed_file(file_name):
            logger.warning(f"File type not allowed: {file_name}")
            return None
        
        if len(file_content) > settings.max_upload_size:
            logger.warning(f"File size exceeds limit: {file_name}")
            return None
        
        FileService.ensure_upload_dir()
        
        file_ext = get_file_extension(file_name)
        unique_filename = f"{user_id}_{file_name}"
        file_path = os.path.join(FileService.UPLOAD_DIR, unique_filename)
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        db_file = FileUpload(
            user_id=user_id,
            filename=file_name,
            file_path=file_path,
            file_size=len(file_content),
            file_type=file_ext
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        logger.info(f"File uploaded: {file_name} by user {user_id}")
        return db_file
    
    @staticmethod
    def get_user_files(db: Session, user_id: str, limit: int = 50) -> list:
        return db.query(FileUpload).filter(FileUpload.user_id == user_id).order_by(FileUpload.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def delete_file(db: Session, file_id: str, user_id: str) -> bool:
        file_upload = db.query(FileUpload).filter(
            FileUpload.id == file_id,
            FileUpload.user_id == user_id
        ).first()
        
        if file_upload:
            if os.path.exists(file_upload.file_path):
                os.remove(file_upload.file_path)
            db.delete(file_upload)
            db.commit()
            logger.info(f"File deleted: {file_id}")
            return True
        return False
