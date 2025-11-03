from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from app.core.dependencies import CurrentUser, SessionDep
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User, UserCreate, UserPublic

router = APIRouter(prefix="/auth", tags=["auth"])


def get_user_by_email(email: str, session: SessionDep) -> User | None:
    """Get a user by email address."""
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


@router.post(
    "/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED
)
def register(user_data: UserCreate, session: SessionDep):
    """
    Register a new user.

    - **email**: Must be unique
    - **password**: Will be hashed before storage
    - **first_name**: User's first name
    - **last_name**: User's last name
    """
    # Check if user already exists
    existing_user = get_user_by_email(user_data.email, session)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Hash the password
    hashed_password = get_password_hash(user_data.password)

    # Create new user
    db_user = User(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        password=hashed_password,
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.post("/login")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
):
    """
    Login endpoint using OAuth2 password flow.

    Returns:
        - **access_token**: JWT token for authentication
        - **token_type**: "bearer"
    """
    # Find user by email (OAuth2PasswordRequestForm uses 'username' field for email)
    user = get_user_by_email(form_data.username, session)

    # Verify user exists and password is correct
    # Always perform password verification to prevent timing attacks
    # Use a dummy hash if user doesn't exist to maintain constant-time verification
    password_valid = False
    if user:
        password_valid = verify_password(form_data.password, user.password)
    else:
        # Perform dummy verification to prevent timing attacks
        # This ensures the response time is similar regardless of user existence
        dummy_hash = "$argon2id$v=19$m=65536,t=3,p=4$dummyhashdata"
        verify_password(form_data.password, dummy_hash)

    if not user or not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(data={"sub": user.email, "user_id": user.id})

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserPublic)
def get_current_user_info(current_user: CurrentUser):
    """
    Get the current authenticated user's information.

    Requires a valid JWT token in the Authorization header.
    """
    return current_user
