from fastapi import HTTPException, status
from app.repositories import payment_link_repo, transaction_repo
from app.schemas.transaction import PaySimulationRequest
from app.db import cache

def simulate_payment(payment_link_id: str, request: PaySimulationRequest) -> dict:
    link = payment_link_repo.get_payment_link_by_id(payment_link_id)
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment link not found"
        )
    
    if link["status"] == "paid":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Payment link has already been paid"
        )
    
    if link["status"] in ("expired", "cancelled"):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail=f"Payment link is {link['status']}"
        )
        
    transaction_status = "failed" if request.simulate_failure else "success"
    
    # Insert the transaction row
    transaction = transaction_repo.create_transaction(
        payment_link_id=payment_link_id,
        merchant_id=str(link["merchant_id"]),
        amount=float(link["amount"]),
        currency=link["currency"],
        status=transaction_status,
        payment_method=request.payment_method
    )
    
    if transaction_status == "success":
        payment_link_repo.update_payment_link_status(payment_link_id, "paid")
        cache.delete(f"payment_link:{payment_link_id}")
        
    return transaction
