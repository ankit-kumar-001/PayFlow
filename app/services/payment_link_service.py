from typing import List, Optional
from datetime import datetime, timedelta, timezone
from app.repositories import payment_link_repo
from app.schemas.payment_link import PaymentLinkCreate

def format_payment_link(link: dict) -> dict:
    if link:
        # Build the pay_url
        link["pay_url"] = f"/pay/{link['id']}"
    return link

def create_payment_link(merchant_id: str, link_in: PaymentLinkCreate) -> dict:
    if link_in.expires_in_minutes:
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=link_in.expires_in_minutes)
    else:
        # Default expiry 24h
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

    link = payment_link_repo.create_payment_link(
        merchant_id=merchant_id,
        amount=float(link_in.amount),
        currency=link_in.currency,
        description=link_in.description,
        expires_at=expires_at,
        status="created"
    )
    return format_payment_link(link)

def get_payment_link(link_id: str) -> Optional[dict]:
    link = payment_link_repo.get_payment_link_by_id(link_id)
    if not link:
        return None
    
    # Check expiry
    if link["status"] == "created" and link["expires_at"]:
        if datetime.now(timezone.utc) > link["expires_at"]:
            # Flip to expired
            link = payment_link_repo.update_payment_link_status(link_id, "expired")
            
    return format_payment_link(link)

def list_merchant_payment_links(merchant_id: str, limit: int = 10, offset: int = 0) -> List[dict]:
    links = payment_link_repo.list_payment_links_by_merchant(merchant_id, limit, offset)
    return [format_payment_link(link) for link in links]
