from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class AnalysisStatus(str, Enum):
    """Enum for analysis job status."""
    PENDING = "pending"
    RUNNING = "running"
    ANALYZING_CODE = "analyzing_code"
    ANALYZING_DEPENDENCIES = "analyzing_dependencies"
    ANALYZING_BUSINESS = "analyzing_business"
    ANALYZING_ARCHITECTURE = "analyzing_architecture"
    COMPLETED = "completed"
    FAILED = "failed"

class AnalysisJobCreationResponse(BaseModel):
    """Response model specifically for the analyze_project endpoint."""
    analysis_id: str
    project_id: str
    status: str
    analysis_types: List[str]
    progress: int = 0
    message: str  

class AnalysisRequest(BaseModel):
    """Request model for starting an analysis job."""
    analysis_types: List[str] = ["code", "dependencies", "business", "architecture"]


class AnalysisCreateRequest(BaseModel):
    """Request model for creating an analysis job."""
    project_id: str
    analysis_types: List[str] = ["code", "dependencies", "business", "architecture"]
    from_repository: bool = False


class AnalysisResponse(BaseModel):
    """Response model for analysis jobs."""
    id: str                              # Renamed from analysis_id to id to match database structure
    project_id: str
    status: str
    analysis_types: List[str]
    progress: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    
    # Optional metadata
    project_name: Optional[str] = None
    file_count: Optional[int] = None
    languages: Optional[List[str]] = None
    


class CodeAnalysisResponse(BaseModel):
    """Response model for code analysis results."""
    language_summaries: Dict[str, Any] = {}
    file_summaries: Dict[str, Any] = {}
    file_count: int
    language_distribution: Dict[str, int]


class DependencyAnalysisResponse(BaseModel):
    """Response model for dependency analysis results."""
    dependencies: str
    dependency_graph: str
    analyzed_files: List[str]


class BusinessAnalysisResponse(BaseModel):
    """Response model for business analysis results."""
    business_functionality: str
    business_entities: Any
    analyzed_files: List[str]


class ArchitectureAnalysisResponse(BaseModel):
    """Response model for architecture analysis results."""
    architecture_analysis: str
    architecture_diagram: str
    analyzed_files: List[str]


class AnalysisResultsResponse(BaseModel):
    """Response model for analysis results."""
    id: str
    project_id: str
    status: str
    analysis_types: List[str]
    progress: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    # Project metadata
    project_name: Optional[str] = None
    file_count: Optional[int] = None
    languages: Optional[List[str]] = None
    
    # Analysis results
    code: Optional[CodeAnalysisResponse] = None
    dependencies: Optional[DependencyAnalysisResponse] = None
    business: Optional[BusinessAnalysisResponse] = None
    architecture: Optional[ArchitectureAnalysisResponse] = None
    
    # Error information
    error: Optional[str] = None

# Step 2: Modify the __init__.py file to expose the models

# services/source-code-service/app/models/__init__.py
# Add this line to expose the models
# from .analysis import (
#     AnalysisStatus, AnalysisRequest, AnalysisCreateRequest, AnalysisResponse,
#     CodeAnalysisResponse, DependencyAnalysisResponse, BusinessAnalysisResponse,
#     ArchitectureAnalysisResponse, AnalysisResultsResponse
# )