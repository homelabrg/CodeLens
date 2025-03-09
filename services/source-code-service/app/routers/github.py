from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel, HttpUrl
import logging
from ..services.github_service import GitHubService
from ..dependencies.service_dependencies import get_github_service

logger = logging.getLogger(__name__)
router = APIRouter()

# Request and response models
class CloneRequest(BaseModel):
    """Request model for cloning a repository."""
    repository_url: HttpUrl
    branch: Optional[str] = "main"
    access_token: Optional[str] = None

class RepositoryResponse(BaseModel):
    """Response model for repository information."""
    id: str
    owner: str
    repo: str
    branch: str
    url: HttpUrl
    status: str
    file_count: Optional[int] = None
    languages: Optional[List[str]] = None
    size_kb: Optional[int] = None

@router.post("/repositories", response_model=RepositoryResponse, status_code=status.HTTP_202_ACCEPTED)
async def clone_repository(
    request: CloneRequest,
    background_tasks: BackgroundTasks,
    github_service: GitHubService = Depends(get_github_service)
):
    """
    Clone a GitHub repository for analysis.
    
    This is an asynchronous operation - the repository will be cloned in the background.
    Check the status using the GET /repositories/{repository_id} endpoint.
    """
    try:
        repository_id = github_service.start_clone(request.repository_url, request.branch, request.access_token)
        
        # Start background task to clone the repository
        background_tasks.add_task(
            github_service.clone_repository,
            repository_id,
            request.repository_url,
            request.branch,
            request.access_token
        )
        
        # Extract owner and repo from URL
        owner, repo = github_service.extract_owner_repo(request.repository_url)
        
        return RepositoryResponse(
            id=repository_id,
            owner=owner,
            repo=repo,
            branch=request.branch,
            url=request.repository_url,
            status="pending"
        )
    except Exception as e:
        logger.error(f"Failed to start repository clone: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start repository clone: {str(e)}"
        )

@router.get("/repositories/{repository_id}", response_model=RepositoryResponse)
async def get_repository_status(
    repository_id: str,
    github_service: GitHubService = Depends(get_github_service)
):
    """
    Get the status of a cloned repository.
    """
    try:
        repo_info = github_service.get_repository_info(repository_id)
        if not repo_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repository with ID {repository_id} not found"
            )
        return repo_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get repository status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get repository status: {str(e)}"
        )

@router.get("/repositories", response_model=List[RepositoryResponse])
async def list_repositories(
    github_service: GitHubService = Depends(get_github_service)
):
    """
    List all repositories that have been cloned.
    """
    try:
        repositories = github_service.list_repositories()
        return repositories
    except Exception as e:
        logger.error(f"Failed to list repositories: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list repositories: {str(e)}"
        )