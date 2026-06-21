from fastapi import HTTPException, status
from app.schemas.user import UserSignup, UserLogin, UserOut, TokenResponse
from app.repositories import user_repo
from app.core import security

def signup(signup_data: UserSignup) -> dict:
    existing_user = user_repo.get_user_by_email(signup_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = security.get_password_hash(signup_data.password)
    user = user_repo.create_user(
        email=signup_data.email,
        password_hash=hashed_password,
        full_name=signup_data.full_name
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    return user

def login(login_data: UserLogin) -> dict:
    user = user_repo.get_user_by_email(login_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not security.verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    access_token = security.create_access_token(subject=user["id"])
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
