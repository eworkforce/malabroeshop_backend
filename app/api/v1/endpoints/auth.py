from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, schemas
from app.db.session import get_db
from app.core.auth import create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.api.v1.endpoints.notification import send_welcome_email, send_admin_new_user_notification

router = APIRouter()

def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    email = verify_token(token)
    if email is None:
        raise credentials_exception
    user = crud.user.get_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_active_admin_user(current_user: schemas.User = Depends(get_current_active_user)):
    if not crud.user.is_admin(current_user):
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges"
        )
    return current_user

@router.post("/register", response_model=schemas.User)
def register_user(
    *, 
    db: Session = Depends(get_db), 
    user_in: schemas.UserCreate,
    background_tasks: BackgroundTasks
) -> Any:
    """
    Register a new user and send welcome/notification emails
    """
    # Check if user already exists
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    # Create new user
    user = crud.user.create(db, obj_in=user_in)
    
    # Format registration date
    from datetime import datetime
    registration_date = user.created_at.strftime('%d/%m/%Y à %H:%M') if user.created_at else datetime.now().strftime('%d/%m/%Y à %H:%M')
    
    # Send email notifications in background (won't block the response)
    try:
        # Welcome email to new user
        background_tasks.add_task(
            send_welcome_email,
            user.email,
            user.full_name,
            registration_date
        )
        
        # Notification email to admin
        background_tasks.add_task(
            send_admin_new_user_notification,
            user.email,
            user.full_name,
            registration_date,
            user.is_active,
            user.is_admin
        )
        
        print(f"✅ Email notifications queued for new user: {user.email}")
        
    except Exception as e:
        # Log error but don't fail registration
        print(f"⚠️ Failed to queue email notifications: {e}")
    
    return user

@router.post("/login", response_model=schemas.Token)
def login_user(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    user = crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "user": user,
    }

@router.get("/me", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(get_current_active_user)) -> Any:
    return current_user
