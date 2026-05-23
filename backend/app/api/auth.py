from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.models.schemas import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    create_user,
    get_current_user,
    get_user_by_email,
)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/register", response_model=UserResponse)
def register_user(
    request: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    existing_user = get_user_by_email(
        db,
        request.email.lower().strip()
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered."
        )

    user = create_user(
        db=db,
        email=request.email,
        password=request.password,
        full_name=request.full_name
    )

    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name
    )


@router.post("/login", response_model=TokenResponse)
def login_user(
    request: UserLoginRequest,
    db: Session = Depends(get_db)
):
    user = authenticate_user(
        db=db,
        email=request.email,
        password=request.password
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email
        }
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name
        )
    )


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name
    )