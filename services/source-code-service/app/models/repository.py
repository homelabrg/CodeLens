# services/source-code-service/app/models/repository.py
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime

class RepositoryInfo(BaseModel):
    """Repository information model"""
    id: str
    owner: str
    repo: str
    url: HttpUrl
    branch: str
    status: str  # pending, cloning, ready, failed
    file_count: Optional[int] = None
    languages: Optional[List[str]] = None
    size_kb: Optional[int] = None
    created_at: datetime
    updated_at: datetime

class RepositoryCreate(BaseModel):
    """Model for creating a new repository record"""
    repository_id: str
    owner: str
    repo: str
    url: str
    branch: str
    status: str

class RepositoryUpdate(BaseModel):
    """Model for updating a repository record"""
    status: Optional[str] = None
    file_count: Optional[int] = None
    languages: Optional[List[str]] = None
    size_kb: Optional[int] = None