from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class Token(BaseModel):
    """Token model for authentication"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Token data model"""
    username: Optional[str] = None

class UserBase(BaseModel):
    """Base user model"""
    username: str

class UserCreate(UserBase):
    """User creation model"""
    password: str

class User(UserBase):
    """User model for responses"""
    disabled: bool = False

    class Config:
        orm_mode = True

class UserInDB(User):
    """User model stored in database"""
    hashed_password: str

class QueryRequest(BaseModel):
    """Model for incoming query requests"""
    query: str

class QueryResultItem(BaseModel):
    """Model for individual result items"""
    # This is flexible to accommodate different result structures
    data: Dict[str, Any]

class QueryResponse(BaseModel):
    """Model for query responses"""
    original_query: str
    translated_query: str
    result: List[QueryResultItem]
    execution_time: float

class ExplanationStep(BaseModel):
    """Model for individual explanation steps"""
    step: str
    detail: str

class ExplanationResponse(BaseModel):
    """Model for explanation responses"""
    original_query: str
    summary: str
    steps: List[ExplanationStep]

class ValidationReason(BaseModel):
    """Model for validation reasons"""
    type: str
    message: str

class ValidationSuggestion(BaseModel):
    """Model for validation suggestions"""
    suggestion: str
    example: Optional[str] = None

class ValidationResponse(BaseModel):
    """Model for validation responses"""
    original_query: str
    is_valid: bool
    reasons: List[ValidationReason]
    suggestions: Optional[List[ValidationSuggestion]] = None

class HealthCheck(BaseModel):
    """Model for health check responses"""
    status: str
    version: str
    database_status: Optional[str] = None