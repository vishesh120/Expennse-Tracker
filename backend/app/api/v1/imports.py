from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from app.repositories.transaction_repo import TransactionRepository
from app.services.import_service import ImportService
from app.core.dependencies import get_transaction_repository, get_current_user

router = APIRouter(prefix="/imports", tags=["Imports"])


@router.post("/csv")
async def import_csv(
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user),
    txn_repo: TransactionRepository = Depends(get_transaction_repository)
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only .csv files are supported."
        )

    # Maximum upload size check (e.g. 5 MB)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the 5MB limit."
        )

    try:
        csv_str = contents.decode("utf-8")
    except UnicodeDecodeError:
        try:
            csv_str = contents.decode("latin-1")
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to decode CSV file. Please ensure UTF-8 encoding."
            )

    service = ImportService(txn_repo)
    result = await service.process_csv_upload(
        user_id=current_user["id"],
        csv_content=csv_str
    )
    return result
