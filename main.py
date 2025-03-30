from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import sqlite3
from query_processor import QueryProcessor

# App configuration
app = FastAPI(
    title="Gen AI Analytics Tool API",
    description="A simulation of Gen AI Analytics data query system",
    version="0.1.0"
)

# Security configuration
SECRET_KEY = "your-secret-key-here"  # In production, use environment variables
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Mock user database
fake_users_db = {
    "analyst": {
        "username": "analyst",
        "hashed_password": pwd_context.hash("analystpass"),
        "disabled": False,
    }
}

# Database connection
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# Initialize query processor
query_processor = QueryProcessor(conn)

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    original_query: str
    translated_query: str
    result: List[Dict[str, Any]]
    execution_time: float

class ExplanationResponse(BaseModel):
    original_query: str
    explanation: str
    steps: List[str]

class ValidationResponse(BaseModel):
    original_query: str
    is_valid: bool
    reasons: List[str]
    suggestions: Optional[List[str]] = None

# Auth functions (from auth.py)
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.now(datetime.timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Auth endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Core API endpoints
@app.post("/query", response_model=QueryResponse)
async def process_query(
    query_request: QueryRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Process a natural language query and return results.
    
    Example queries:
    - "Show me the top 5 customers by revenue"
    - "What were our sales last quarter?"
    - "List products with inventory below 100 units"
    """
    try:
        result = query_processor.process_query(query_request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/explain", response_model=ExplanationResponse)
async def explain_query(
    query_request: QueryRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Explain how a natural language query would be processed.
    """
    try:
        explanation = query_processor.explain_query(query_request.query)
        return explanation
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/validate", response_model=ValidationResponse)
async def validate_query(
    query_request: QueryRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Validate if a natural language query can be processed.
    """
    try:
        validation = query_processor.validate_query(query_request.query)
        return validation
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}