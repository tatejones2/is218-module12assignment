# app/operations/calculations.py

"""
Calculation operations module for handling calculation-related business logic.
"""

from uuid import UUID
from sqlalchemy.orm import Session
from app.models.calculation import Calculation
from app.schemas.calculation import CalculationBase, CalculationUpdate


class CalculationOperations:
    """Calculation operations class for managing calculation-related database operations."""
    
    @staticmethod
    def create_calculation(
        db: Session,
        user_id: UUID,
        calculation_type: str,
        inputs: dict
    ) -> Calculation:
        """
        Create and persist a new calculation.
        
        Args:
            db: SQLAlchemy database session
            user_id: User's UUID who owns the calculation
            calculation_type: Type of calculation (add, subtract, multiply, divide)
            inputs: Dictionary containing calculation inputs
            
        Returns:
            Calculation: The newly created calculation instance
            
        Raises:
            ValueError: If calculation type is invalid or inputs are invalid
        """
        try:
            # Create the calculation using the factory method
            calculation = Calculation.create(
                calculation_type=calculation_type,
                user_id=user_id,
                inputs=inputs,
            )
            # Compute result
            calculation.result = calculation.get_result()
            
            # Persist to database
            db.add(calculation)
            db.commit()
            db.refresh(calculation)
            return calculation
        except ValueError as e:
            db.rollback()
            raise ValueError(f"Failed to create calculation: {str(e)}")
    
    @staticmethod
    def list_user_calculations(db: Session, user_id: UUID) -> list:
        """
        List all calculations for a specific user.
        
        Args:
            db: SQLAlchemy database session
            user_id: User's UUID
            
        Returns:
            list: List of Calculation instances for the user
        """
        calculations = db.query(Calculation).filter(
            Calculation.user_id == user_id
        ).all()
        return calculations
    
    @staticmethod
    def get_calculation_by_id(db: Session, calc_id: UUID, user_id: UUID) -> Calculation:
        """
        Retrieve a specific calculation by ID.
        
        Args:
            db: SQLAlchemy database session
            calc_id: Calculation's UUID
            user_id: User's UUID (for authorization)
            
        Returns:
            Calculation: The calculation instance
            
        Raises:
            ValueError: If calculation not found or user is not the owner
        """
        calculation = db.query(Calculation).filter(
            Calculation.id == calc_id,
            Calculation.user_id == user_id
        ).first()
        
        if not calculation:
            raise ValueError(
                f"Calculation with ID {calc_id} not found or access denied"
            )
        return calculation
    
    @staticmethod
    def update_calculation(
        db: Session,
        calc_id: UUID,
        user_id: UUID,
        update_data: CalculationUpdate
    ) -> Calculation:
        """
        Update a calculation's inputs and recompute result.
        
        Args:
            db: SQLAlchemy database session
            calc_id: Calculation's UUID
            user_id: User's UUID (for authorization)
            update_data: CalculationUpdate schema with fields to update
            
        Returns:
            Calculation: The updated calculation instance
            
        Raises:
            ValueError: If calculation not found or update fails
        """
        calculation = CalculationOperations.get_calculation_by_id(
            db, calc_id, user_id
        )
        
        # Update inputs if provided
        if update_data.inputs is not None:
            try:
                calculation.inputs = update_data.inputs
                calculation.result = calculation.get_result()
            except ValueError as e:
                db.rollback()
                raise ValueError(f"Failed to update calculation: {str(e)}")
        
        db.commit()
        db.refresh(calculation)
        return calculation
    
    @staticmethod
    def delete_calculation(db: Session, calc_id: UUID, user_id: UUID) -> None:
        """
        Delete a calculation.
        
        Args:
            db: SQLAlchemy database session
            calc_id: Calculation's UUID
            user_id: User's UUID (for authorization)
            
        Raises:
            ValueError: If calculation not found
        """
        calculation = CalculationOperations.get_calculation_by_id(
            db, calc_id, user_id
        )
        db.delete(calculation)
        db.commit()
    
    @staticmethod
    def get_calculation_count(db: Session, user_id: UUID) -> int:
        """
        Get the count of calculations for a user.
        
        Args:
            db: SQLAlchemy database session
            user_id: User's UUID
            
        Returns:
            int: Number of calculations
        """
        count = db.query(Calculation).filter(
            Calculation.user_id == user_id
        ).count()
        return count
    
    @staticmethod
    def get_calculation_by_type(
        db: Session,
        user_id: UUID,
        calculation_type: str
    ) -> list:
        """
        Get all calculations of a specific type for a user.
        
        Args:
            db: SQLAlchemy database session
            user_id: User's UUID
            calculation_type: Type of calculation to filter by
            
        Returns:
            list: List of Calculation instances matching the type
        """
        calculations = db.query(Calculation).filter(
            Calculation.user_id == user_id,
            Calculation.type == calculation_type
        ).all()
        return calculations
    
    @staticmethod
    def clear_user_calculations(db: Session, user_id: UUID) -> int:
        """
        Delete all calculations for a user.
        
        Args:
            db: SQLAlchemy database session
            user_id: User's UUID
            
        Returns:
            int: Number of calculations deleted
        """
        count = db.query(Calculation).filter(
            Calculation.user_id == user_id
        ).delete()
        db.commit()
        return count
