from typing import List, Dict, Any, Optional
from pydantic import BaseModel

# Database schemas
class CustomerBase(BaseModel):
    """Base customer schema"""
    name: str
    email: str

class CustomerCreate(CustomerBase):
    """Customer creation schema"""
    revenue: float
    region: str

class Customer(CustomerBase):
    """Customer schema for responses"""
    id: int
    revenue: float
    region: str
    join_date: str

    class Config:
        orm_mode = True

class ProductBase(BaseModel):
    """Base product schema"""
    name: str
    category: str

class ProductCreate(ProductBase):
    """Product creation schema"""
    price: float
    inventory: int

class Product(ProductBase):
    """Product schema for responses"""
    id: int
    price: float
    inventory: int
    supplier: Optional[str] = None

    class Config:
        orm_mode = True

class SaleBase(BaseModel):
    """Base sale schema"""
    amount: float
    date: str

class SaleCreate(SaleBase):
    """Sale creation schema"""
    product_id: int
    customer_id: int
    region: str

class Sale(SaleBase):
    """Sale schema for responses"""
    id: int
    product_id: int
    customer_id: int
    region: str

    class Config:
        orm_mode = True

class EmployeeBase(BaseModel):
    """Base employee schema"""
    name: str
    department: str

class EmployeeCreate(EmployeeBase):
    """Employee creation schema"""
    salary: float

class Employee(EmployeeBase):
    """Employee schema for responses"""
    id: int
    salary: float
    hire_date: str

    class Config:
        orm_mode = True

# Analytics schemas
class AnalyticsQuery(BaseModel):
    """Base analytics query schema"""
    query: str
    user_id: Optional[int] = None

class AnalyticsResult(BaseModel):
    """Analytics result schema"""
    columns: List[str]
    data: List[Dict[str, Any]]
    query_execution_time: float

class QueryExplanation(BaseModel):
    """Query explanation schema"""
    original_query: str
    parsed_components: Dict[str, str]
    sql_translation: str
    confidence_score: float

class QueryValidation(BaseModel):
    """Query validation schema"""
    is_valid: bool
    validation_errors: Optional[List[str]] = None
    suggested_improvements: Optional[List[str]] = None