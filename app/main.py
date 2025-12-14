from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from uuid import UUID
from typing import List
from fastapi import Body, FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user, get_current_user
from app.models.calculation import Calculation
from app.models.user import User
from app.schemas.calculation import CalculationBase, CalculationResponse, CalculationUpdate
from app.schemas.token import TokenResponse
from app.schemas.user import UserCreate, UserResponse, UserLogin, UserUpdate, PasswordUpdate
from app.operations.users import UserOperations
from app.database import Base, get_db, engine

# Create tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
    yield

app = FastAPI(
    title="Calculations API",
    description="API for managing calculations",
    version="1.0.0",
    lifespan=lifespan
)

# ------------------------------------------------------------------------------
# Health Endpoint
# ------------------------------------------------------------------------------
@app.get("/health", tags=["health"])
def read_health():
    return {"status": "ok"}

# ===============================================================================
# User Endpoints
# ===============================================================================

# Register a new user
@app.post(
    "/users/register", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED,
    tags=["users"],
    summary="Register a new user",
    description="Create a new user account with email, username, and password"
)
def register_user(user_create: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.
    
    - **first_name**: User's first name (1-50 characters)
    - **last_name**: User's last name (1-50 characters)
    - **email**: User's email address (must be unique)
    - **username**: User's username (3-50 characters, must be unique)
    - **password**: Password with at least 8 characters, uppercase, lowercase, digit, and special character
    - **confirm_password**: Password confirmation (must match password)
    """
    try:
        user = UserOperations.register_user(db, user_create)
        db.commit()
        db.refresh(user)
        return user
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# Login user and get tokens
@app.post(
    "/users/login", 
    response_model=TokenResponse, 
    tags=["users"],
    summary="Login user",
    description="Authenticate a user and receive access and refresh tokens"
)
def login_user(user_login: UserLogin, db: Session = Depends(get_db)):
    """
    Login user with username/email and password.
    
    Returns access and refresh tokens along with user information.
    
    - **username**: Username or email address
    - **password**: User's password
    """
    try:
        auth_result = UserOperations.authenticate_user(db, user_login.username, user_login.password)
        db.commit()  # Commit the last_login update
        
        user = auth_result["user"]
        
        # Ensure expires_at is timezone-aware
        expires_at = auth_result.get("expires_at")
        if expires_at and expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        else:
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
        
        return TokenResponse(
            access_token=auth_result["access_token"],
            refresh_token=auth_result["refresh_token"],
            token_type="bearer",
            expires_at=expires_at,
            user_id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            is_verified=user.is_verified
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

# Get current user profile
@app.get(
    "/users/me",
    response_model=UserResponse,
    tags=["users"],
    summary="Get current user profile",
    description="Retrieve the authenticated user's profile information"
)
def get_current_user_profile(current_user: UserResponse = Depends(get_current_active_user)):
    """
    Get the current authenticated user's profile information.
    
    Requires a valid JWT access token in the Authorization header.
    """
    return current_user

# Get user by ID (admin or self)
@app.get(
    "/users/{user_id}",
    response_model=UserResponse,
    tags=["users"],
    summary="Get user by ID",
    description="Retrieve a specific user's public profile information"
)
def get_user(user_id: str, db: Session = Depends(get_db)):
    """
    Get a user's profile by ID.
    
    - **user_id**: User's UUID
    """
    try:
        user = UserOperations.get_user_by_id(db, UUID(user_id))
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

# Update user profile
@app.put(
    "/users/{user_id}",
    response_model=UserResponse,
    tags=["users"],
    summary="Update user profile",
    description="Update the authenticated user's profile information"
)
def update_user_profile(
    user_id: str,
    user_update: UserUpdate,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a user's profile information.
    
    Users can only update their own profile. Admin users can update any profile.
    
    - **first_name**: User's first name (optional)
    - **last_name**: User's last name (optional)
    - **email**: User's email address (optional, must be unique)
    - **username**: User's username (optional, must be unique)
    """
    # Check if user is updating their own profile or is an admin
    if str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile"
        )
    
    try:
        user = UserOperations.update_user(db, user_id, user_update)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# Change password
@app.post(
    "/users/{user_id}/change-password",
    response_model=UserResponse,
    tags=["users"],
    summary="Change user password",
    description="Change the authenticated user's password"
)
def change_user_password(
    user_id: str,
    password_data: PasswordUpdate,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change a user's password.
    
    Requires the current password for verification.
    
    - **current_password**: The user's current password
    - **new_password**: The new password to set
    - **confirm_new_password**: Confirmation of the new password
    """
    # Check if user is changing their own password
    if str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only change your own password"
        )
    
    try:
        user = UserOperations.change_password(db, user_id, password_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# Deactivate user account
@app.post(
    "/users/{user_id}/deactivate",
    response_model=UserResponse,
    tags=["users"],
    summary="Deactivate user account",
    description="Deactivate the authenticated user's account"
)
def deactivate_user_account(
    user_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Deactivate a user account.
    
    Users can only deactivate their own account.
    """
    # Check if user is deactivating their own account
    if str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only deactivate your own account"
        )
    
    try:
        user = UserOperations.deactivate_user(db, user_id)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

# Delete user account
@app.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["users"],
    summary="Delete user account",
    description="Permanently delete the authenticated user's account"
)
def delete_user_account(
    user_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a user account permanently.
    
    Users can only delete their own account. This action cannot be undone.
    """
    # Check if user is deleting their own account
    if str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account"
        )
    
    try:
        UserOperations.delete_user(db, user_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

# ===============================================================================
# Legacy Auth Endpoints (for backward compatibility)
# ===============================================================================

@app.post("/auth/token", tags=["auth"])
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login with form data for Swagger UI (legacy endpoint)"""
    try:
        auth_result = UserOperations.authenticate_user(db, form_data.username, form_data.password)
        db.commit()
        return {
            "access_token": auth_result["access_token"],
            "token_type": "bearer"
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ------------------------------------------------------------------------------
# Calculations Endpoints (BREAD)
# ------------------------------------------------------------------------------
# Create (Add) Calculation – using CalculationBase so that 'user_id' from the client is ignored.
@app.post(
    "/calculations",
    response_model=CalculationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["calculations"],
)
def create_calculation(
    calculation_data: CalculationBase,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Compute and persist a calculation.
    
    The endpoint reads the calculation type and inputs from the request (ignoring any extra fields),
    computes the result using the appropriate operation, and assigns the authenticated user's ID.
    """
    try:
        # Create the calculation using the factory method.
        new_calculation = Calculation.create(
            calculation_type=calculation_data.type,
            user_id=current_user.id,
            inputs=calculation_data.inputs,
        )
        new_calculation.result = new_calculation.get_result()

        # Persist the calculation to the database.
        db.add(new_calculation)
        db.commit()
        db.refresh(new_calculation)
        return new_calculation

    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Browse / List Calculations (for the current user)
@app.get("/calculations", response_model=List[CalculationResponse], tags=["calculations"])
def list_calculations(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    calculations = db.query(Calculation).filter(Calculation.user_id == current_user.id).all()
    return calculations

# Read / Retrieve a Specific Calculation by ID
@app.get("/calculations/{calc_id}", response_model=CalculationResponse, tags=["calculations"])
def get_calculation(
    calc_id: str,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    try:
        calc_uuid = UUID(calc_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid calculation id format.")
    calculation = db.query(Calculation).filter(
        Calculation.id == calc_uuid,
        Calculation.user_id == current_user.id
    ).first()
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found.")
    return calculation

# Edit / Update a Calculation
@app.put("/calculations/{calc_id}", response_model=CalculationResponse, tags=["calculations"])
def update_calculation(
    calc_id: str,
    calculation_update: CalculationUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    try:
        calc_uuid = UUID(calc_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid calculation id format.")
    calculation = db.query(Calculation).filter(
        Calculation.id == calc_uuid,
        Calculation.user_id == current_user.id
    ).first()
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found.")

    if calculation_update.inputs is not None:
        calculation.inputs = calculation_update.inputs
        calculation.result = calculation.get_result()
    calculation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(calculation)
    return calculation

# Delete a Calculation
@app.delete("/calculations/{calc_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["calculations"])
def delete_calculation(
    calc_id: str,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    try:
        calc_uuid = UUID(calc_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid calculation id format.")
    calculation = db.query(Calculation).filter(
        Calculation.id == calc_uuid,
        Calculation.user_id == current_user.id
    ).first()
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found.")
    db.delete(calculation)
    db.commit()
    return None

# ------------------------------------------------------------------------------
# Main Block to Run the Server
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8001, log_level="info")
