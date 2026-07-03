from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.transaction import PaySimulationRequest, TransactionOut
from app.services import payment_service
from app.repositories import transaction_repo
from app.core.dependencies import get_current_merchant

router = APIRouter(tags=["payments"])

@router.post("/payment-links/{link_id}/pay", response_model=TransactionOut, status_code=201)
def pay_payment_link(link_id: str, request: PaySimulationRequest):
    """
    Simulate paying a payment link (public endpoint).
    """
    return payment_service.simulate_payment(link_id, request)

@router.get("/transactions/{transaction_id}", response_model=TransactionOut)
def get_transaction(
    transaction_id: str,
    current_merchant: dict = Depends(get_current_merchant)
):
    """
    Get a transaction by ID (Merchant-authenticated).
    """
    transaction = transaction_repo.get_transaction_by_id(transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
        
    if str(transaction["merchant_id"]) != str(current_merchant["id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Transaction does not belong to this merchant"
        )
        
    return transaction
