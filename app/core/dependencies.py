from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from app.core.config import settings
from app.repositories.user_repo import get_user_by_id
from app.repositories.merchant_repo import get_merchant_by_api_key
from app.core.security import verify_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user

def get_current_merchant(
    x_api_key: str = Header(..., alias="X-API-Key"),
    x_api_secret: str = Header(..., alias="X-API-Secret")
) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API Key or Secret",
    )
    
    merchant = get_merchant_by_api_key(x_api_key)
    if not merchant:
        raise credentials_exception
        
    if merchant["status"] != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Merchant account is inactive"
        )
        
    if not verify_password(x_api_secret, merchant["api_secret_hash"]):
        raise credentials_exception
        
    return merchant
