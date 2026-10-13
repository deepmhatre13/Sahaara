import os
import shutil
import tempfile
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.api.deps import ensure_self, get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.report import MedicalDocumentOut
from app.services import report_service

router = APIRouter(prefix="/reports", tags=["reports"])

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/{user_id}/upload", response_model=MedicalDocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_report(
    user_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_self(current_user, user_id)

    raw_filename = file.filename or "uploaded_report"
    safe_basename = Path(raw_filename).name
    extension = Path(safe_basename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{extension}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    temp_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}_{safe_basename}")
    size = 0
    try:
        with open(temp_path, "wb") as buffer:
            while chunk := await file.read(1024 * 64):
                size += len(chunk)
                if size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="File exceeds maximum allowed size of 10MB",
                    )
                buffer.write(chunk)

        return report_service.analyze_report(db, user_id, temp_path, safe_basename)
    except HTTPException:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        raise
    except Exception as exc:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process medical report",
        ) from exc


@router.get("/{user_id}", response_model=list[MedicalDocumentOut])
def list_reports(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_self(current_user, user_id)
    return report_service.list_documents(db, user_id)