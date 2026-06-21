from fastapi import APIRouter
from app.schemas.user import UserSignup, UserLogin, UserOut, TokenResponse
from app.services import auth_service
from app.core.dependencies import get_current_user
from fastapi import Depends

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserOut)
def signup(signup_data: UserSignup):
    return auth_service.signup(signup_data)

@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin):
    return auth_service.login(login_data)

@router.get("/me", response_model=UserOut)
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user
