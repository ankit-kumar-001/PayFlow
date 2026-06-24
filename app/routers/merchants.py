from typing import List
from fastapi import APIRouter, Depends
from app.schemas.merchant import MerchantCreate, MerchantOut, MerchantCreateOut
from app.services.merchant_service import create_merchant
from app.repositories.merchant_repo import get_merchants_by_user_id
from app.core.dependencies import get_current_user, get_current_merchant

router = APIRouter(prefix="/merchants", tags=["merchants"])

@router.post("", response_model=MerchantCreateOut, status_code=201)
def create_merchant_endpoint(
    merchant_in: MerchantCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Creates a new merchant account for the current user.
    """
    return create_merchant(
        user_id=current_user["id"],
        business_name=merchant_in.business_name
    )

@router.get("/me", response_model=List[MerchantOut])
def get_my_merchants(current_user: dict = Depends(get_current_user)):
    """
    Retrieves all merchants owned by the current user.
    """
    return get_merchants_by_user_id(str(current_user["id"]))

@router.get("/ping")
def ping_merchant(current_merchant: dict = Depends(get_current_merchant)):
    """
    Test endpoint to verify API key authentication.
    """
    return {"message": "pong", "merchant_id": str(current_merchant["id"])}
