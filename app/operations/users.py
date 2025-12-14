# app/operations/users.py

"""
User operations module for handling user-related business logic.
"""

from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate, PasswordUpdate


class UserOperations:
    """User operations class for managing user-related database operations."""
    
    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> User:
        """
        Register a new user.
        
        Args:
            db: SQLAlchemy database session
            user_data: UserCreate schema with registration data
            
        Returns:
            User: The newly created user instance
            
        Raises:
            ValueError: If username/email already exists or data is invalid
        """
        user_dict = user_data.dict(exclude={"confirm_password"})
        return User.register(db, user_dict)
    
    @staticmethod
    def authenticate_user(db: Session, username_or_email: str, password: str) -> dict:
        """
        Authenticate a user by username/email and password.
        
        Args:
            db: SQLAlchemy database session
            username_or_email: Username or email to authenticate
            password: Password to verify
            
        Returns:
            dict: Authentication result with tokens and user data
            
        Raises:
            ValueError: If authentication fails
        """
        auth_result = User.authenticate(db, username_or_email, password)
        if auth_result is None:
            raise ValueError("Invalid username or password")
        return auth_result
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> User:
        """
        Get a user by their ID.
        
        Args:
            db: SQLAlchemy database session
            user_id: User's unique identifier (UUID)
            
        Returns:
            User: The user instance
            
        Raises:
            ValueError: If user not found
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        return user
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User:
        """
        Get a user by their username.
        
        Args:
            db: SQLAlchemy database session
            username: User's username
            
        Returns:
            User: The user instance
            
        Raises:
            ValueError: If user not found
        """
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise ValueError(f"User with username '{username}' not found")
        return user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User:
        """
        Get a user by their email.
        
        Args:
            db: SQLAlchemy database session
            email: User's email address
            
        Returns:
            User: The user instance
            
        Raises:
            ValueError: If user not found
        """
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise ValueError(f"User with email '{email}' not found")
        return user
    
    @staticmethod
    def update_user(db: Session, user_id: str, update_data: UserUpdate) -> User:
        """
        Update user information.
        
        Args:
            db: SQLAlchemy database session
            user_id: User's unique identifier (UUID)
            update_data: UserUpdate schema with fields to update
            
        Returns:
            User: The updated user instance
            
        Raises:
            ValueError: If user not found or update fails
        """
        user = UserOperations.get_user_by_id(db, user_id)
        
        # Only update fields that are provided
        update_dict = update_data.dict(exclude_unset=True)
        
        # Check if username or email already exists (if being updated)
        if "username" in update_dict:
            existing = db.query(User).filter(
                User.username == update_dict["username"],
                User.id != user_id
            ).first()
            if existing:
                raise ValueError("Username already exists")
        
        if "email" in update_dict:
            existing = db.query(User).filter(
                User.email == update_dict["email"],
                User.id != user_id
            ).first()
            if existing:
                raise ValueError("Email already exists")
        
        # Update user fields
        user.update(**update_dict)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def change_password(db: Session, user_id: str, password_data: PasswordUpdate) -> User:
        """
        Change a user's password.
        
        Args:
            db: SQLAlchemy database session
            user_id: User's unique identifier (UUID)
            password_data: PasswordUpdate schema with old and new passwords
            
        Returns:
            User: The updated user instance
            
        Raises:
            ValueError: If current password is incorrect or user not found
        """
        user = UserOperations.get_user_by_id(db, user_id)
        
        # Verify current password
        if not user.verify_password(password_data.current_password):
            raise ValueError("Current password is incorrect")
        
        # Hash and update password
        new_hashed_password = User.hash_password(password_data.new_password)
        user.password = new_hashed_password
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def deactivate_user(db: Session, user_id: str) -> User:
        """
        Deactivate a user account.
        
        Args:
            db: SQLAlchemy database session
            user_id: User's unique identifier (UUID)
            
        Returns:
            User: The deactivated user instance
            
        Raises:
            ValueError: If user not found
        """
        user = UserOperations.get_user_by_id(db, user_id)
        user.is_active = False
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def activate_user(db: Session, user_id: str) -> User:
        """
        Activate a deactivated user account.
        
        Args:
            db: SQLAlchemy database session
            user_id: User's unique identifier (UUID)
            
        Returns:
            User: The activated user instance
            
        Raises:
            ValueError: If user not found
        """
        user = UserOperations.get_user_by_id(db, user_id)
        user.is_active = True
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def delete_user(db: Session, user_id: str) -> None:
        """
        Delete a user account.
        
        Args:
            db: SQLAlchemy database session
            user_id: User's unique identifier (UUID)
            
        Raises:
            ValueError: If user not found
        """
        user = UserOperations.get_user_by_id(db, user_id)
        db.delete(user)
        db.commit()
