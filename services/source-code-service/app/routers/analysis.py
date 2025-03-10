# services/source-code-service/app/routers/analysis.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status, Query
from typing import List, Optional, Dict, Any
import logging
import uuid
import os
from datetime import datetime  # Add this import

from ..services.analysis_service import AnalysisService
from ..dependencies.service_dependencies import get_analysis_service, get_file_service
from ..services.file_service import FileService
from ..services.openai_service import OpenAIService
from ..dependencies.service_dependencies import get_openai_service
from ..core.config import settings
from ..core.logger import setup_logging
from pydantic import BaseModel
from ..models.analysis import (
    AnalysisResponse, 
    AnalysisResultsResponse, 
    AnalysisRequest,
    AnalysisJobCreationResponse
)
from ..utils.analysis_formatter import format_analysis_results, extract_key_findings


# Setup logging
logger = logging.getLogger(__name__)
router = APIRouter()

class AnalysisResponse(BaseModel):
    """Response model for analysis jobs."""
    analysis_id: str
    project_id: str
    status: str
    analysis_types: List[str]
    progress: int = 0
    message: str

class AnalysisRequest(BaseModel):
    """Request model for starting an analysis job."""
    analysis_types: List[str] = ["code", "dependencies", "business", "architecture"]

class CodeAnalysisRequest(BaseModel):
    code: str
    language: str
    filename: Optional[str] = None

class CodeAnalysisResponse(BaseModel):
    summary: str
    language: str
    complexity: Optional[str] = None
    suggestions: Optional[str] = None
    
@router.post("/code", response_model=CodeAnalysisResponse)
async def analyze_code(
    request: CodeAnalysisRequest,
    openai_service: OpenAIService = Depends(get_openai_service)
):
    """
    Analyze code using OpenAI.
    
    This endpoint takes a code snippet and returns an analysis including:
    - A summary of what the code does
    - Assessment of code complexity
    - Suggestions for improvements
    """
    try:
        # Create prompt
        prompt = f"""
        Analyze the following {request.language} code snippet:

        ```{request.language}
        {request.code}"""

        # Generate a unique ID for this analysis
        analysis_id = str(uuid.uuid4())
    
        # Get analysis from OpenAI
        analysis = await openai_service.analyze_text(prompt)
    
        # Parse analysis into structured response
        summary = ""
        complexity = ""
        suggestions = ""
        
        for line in analysis.split('\n'):
            if line.startswith('- Summary:'):
                summary = line.replace('- Summary:', '').strip()
            elif line.startswith('- Complexity:'):
                complexity = line.replace('- Complexity:', '').strip()
            elif line.startswith('- Suggestions:'):
                suggestions = line.replace('- Suggestions:', '').strip()
        
        # If parsing failed, use the whole response as summary
        if not summary:
            summary = analysis
        
        return CodeAnalysisResponse(
            analysis_id=analysis_id,
            summary=summary,
            language=request.language,
            complexity=complexity,
            suggestions=suggestions
        )
    except Exception as e:
        logger.error(f"Error analyzing code: {str(e)}", exc_info=True)
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Error analyzing code: {str(e)}")
        
async def import_repository_files(repository_id: str) -> Optional[str]:
    """
    Import files from a repository to a new project.
    
    Args:
        repository_id: Repository ID
        
    Returns:
        Optional[str]: New project ID or None if import failed
    """
    from ..services.github_service import GitHubService
    from ..services.file_service import FileService
    from ..dependencies.service_dependencies import get_github_service, get_file_service
    
    try:
        # Get services
        github_service = get_github_service()
        file_service = get_file_service()
        
        # Get repository info
        repo_info = github_service.get_repository_info(repository_id)
        if not repo_info:
            logger.error(f"Repository not found: {repository_id}")
            return None
        
        if repo_info["status"] != "ready":
            logger.error(f"Repository not ready: {repository_id}, status: {repo_info['status']}")
            return None
        
        # Import repository files to a new project
        logger.info(f"Importing files from repository {repository_id} to a new project")
        
        # Create a new project
        project_id = str(uuid.uuid4())
        project_name = f"{repo_info['owner']}/{repo_info['repo']}"
        description = f"Imported from GitHub repository {repo_info['owner']}/{repo_info['repo']}"
        
        # Create project in file service
        file_service.create_project(
            project_id=project_id,
            name=project_name,
            description=description,
            status="importing"
        )
        
        # Copy files from repository to project
        repo_path = os.path.join(settings.CLONE_BASE_PATH, repository_id)
        project_path = os.path.join(settings.FILES_BASE_PATH, project_id)
        
        # Create project directory
        os.makedirs(project_path, exist_ok=True)
        
        # Copy all files (excluding .git directory)
        import shutil
        for item in os.listdir(repo_path):
            if item == ".git":
                continue
                
            source = os.path.join(repo_path, item)
            dest = os.path.join(project_path, item)
            
            if os.path.isdir(source):
                shutil.copytree(source, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(source, dest)
        
        # Process the copied files to update project metadata
        file_service.process_project_files(project_id)
        
        logger.info(f"Successfully imported files from repository {repository_id} to project {project_id}")
        return project_id
        
    except Exception as e:
        logger.error(f"Failed to import repository files: {str(e)}", exc_info=True)
        return None

# Update the analyze_project endpoint to use the correct response model
@router.post("/projects/{project_id}/analyze", response_model=AnalysisJobCreationResponse)
async def analyze_project(
    project_id: str,
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    from_repository: bool = Query(False, description="Whether to import files from a repository"),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """Start analysis of a project."""
    try:
        # If from_repository is True, we need to:
        # 1. Check if the repository exists
        # 2. Import the repository files to a new project
        # 3. Use the new project ID for analysis
        
        actual_project_id = project_id
        
        if from_repository:
            # Import files from repository to a new project
            # This should return the new project ID
            new_project_id = await import_repository_files(project_id)
            if new_project_id:
                actual_project_id = new_project_id
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to import files from repository {project_id}"
                )
        
        # Create analysis job with the correct project ID
        analysis_id = analysis_service.create_analysis_job(
            project_id=actual_project_id,
            analysis_types=request.analysis_types
        )
        
        # Start analysis in background
        background_tasks.add_task(
            analysis_service.run_analysis,
            analysis_id=analysis_id,
            project_id=actual_project_id,
            analysis_types=request.analysis_types
        )
        
        # Return the formatted response
        return AnalysisJobCreationResponse(
            analysis_id=analysis_id,
            project_id=actual_project_id,
            status="pending",
            analysis_types=request.analysis_types,
            progress=0,
            message="Analysis job created. Check status using the analysis_id."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create analysis job: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create analysis job: {str(e)}"
        )

@router.get("/analysis/{analysis_id}")
async def get_analysis_status(
    analysis_id: str,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Get the status of an analysis job.
    
    Args:
        analysis_id: Analysis job ID
        
    Returns:
        Dict: Analysis job information
    """
    try:
        # Get the analysis data
        analysis_info = analysis_service.get_analysis_job(analysis_id)
        if not analysis_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis job with ID {analysis_id} not found"
            )

        # Instead of using the Pydantic model directly, adapt the data to match what's expected
        # This avoids issues with schema mismatches until we can update all schemas
        adapted_response = {
            "analysis_id": analysis_info.get("id"),  # Map id to analysis_id
            "project_id": analysis_info.get("project_id"),
            "status": analysis_info.get("status"),
            "analysis_types": analysis_info.get("analysis_types", []),
            "progress": analysis_info.get("progress", 0),
            "message": f"Analysis status: {analysis_info.get('status')}"  # Add a message field
        }
        
        # Return the adapted response directly without model validation
        return adapted_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analysis status: {str(e)}"
        )


@router.get("/analysis/{analysis_id}/results", response_model=AnalysisResultsResponse)
async def get_detailed_analysis_results(
    analysis_id: str,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Get detailed results of an analysis job.
    
    Args:
        analysis_id: Analysis job ID
        
    Returns:
        AnalysisResultsResponse: Detailed analysis results
    """
    try:
        # Get analysis job info
        analysis_info = analysis_service.get_analysis_job(analysis_id)
        if not analysis_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis job with ID {analysis_id} not found"
            )
        
        # Check if analysis is completed
        if analysis_info["status"] != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Analysis job is not yet completed. Current status: {analysis_info['status']}"
            )
        
        # Get analysis results
        results = analysis_service.get_analysis_results(analysis_id)
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis results not found for analysis {analysis_id}"
            )
        
        # Combine analysis info and results
        analysis_data = {**analysis_info, "results": results}
        
        # Format results using our utility
        formatted_results = format_analysis_results(analysis_data)
        
        return formatted_results
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis results: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analysis results: {str(e)}"
        )

@router.get("/analysis/{analysis_id}/summary")
async def get_analysis_summary(
    analysis_id: str,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Get a summary of analysis results.
    
    Args:
        analysis_id: Analysis job ID
        
    Returns:
        Dict: Summary of analysis findings
    """
    try:
        # Get detailed results
        analysis_info = analysis_service.get_analysis_job(analysis_id)
        if not analysis_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis job with ID {analysis_id} not found"
            )
        
        # Check if analysis is completed
        if analysis_info["status"] != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Analysis job is not yet completed. Current status: {analysis_info['status']}"
            )
        
        # Get analysis results
        results = analysis_service.get_analysis_results(analysis_id)
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis results not found for analysis {analysis_id}"
            )
        
        # Combine analysis info and results
        analysis_data = {**analysis_info, "results": results}
        
        # Format results
        formatted_results = format_analysis_results(analysis_data)
        
        # Extract key findings
        summary = extract_key_findings(formatted_results)
        
        return summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis summary: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analysis summary: {str(e)}"
        )

@router.get("/projects/{project_id}/analysis")
async def list_project_analyses(
    project_id: str,
    analysis_service: AnalysisService = Depends(get_analysis_service),
    file_service: FileService = Depends(get_file_service)
):
    """
    List all analysis jobs for a project.
    
    Args:
        project_id: Project ID
        
    Returns:
        List[Dict]: List of analysis jobs
    """
    try:
        # Check if project exists
        project = file_service.get_project(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        
        # Get analysis jobs
        analyses = analysis_service.list_project_analyses(project_id)
        return analyses
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list project analyses: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list project analyses: {str(e)}"
        )

@router.get("/projects/{project_id}/analysis/latest")
async def get_latest_analysis(
    project_id: str,
    analysis_type: Optional[str] = None,
    analysis_service: AnalysisService = Depends(get_analysis_service),
    file_service: FileService = Depends(get_file_service)
):
    """
    Get the latest analysis for a project.
    
    Args:
        project_id: Project ID
        analysis_type: Type of analysis (optional)
        
    Returns:
        Dict: Analysis information
    """
    try:
        # Check if project exists
        project = file_service.get_project(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        
        # Get latest analysis
        analysis = analysis_service.get_latest_analysis(project_id, analysis_type)
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No analysis found for project {project_id}"
            )
        
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get latest analysis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get latest analysis: {str(e)}"
        )

@router.get("/projects/{project_id}/analysis/results")
async def get_analysis_results(
    project_id: str,
    analysis_id: Optional[str] = None,
    analysis_type: Optional[str] = None,
    analysis_service: AnalysisService = Depends(get_analysis_service),
    file_service: FileService = Depends(get_file_service)
):
    """
    Get the results of an analysis.
    
    Args:
        project_id: Project ID
        analysis_id: Analysis ID (optional)
        analysis_type: Type of analysis (optional)
        
    Returns:
        Dict: Analysis results
    """
    try:
        # Check if project exists
        project = file_service.get_project(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        
        # Get analysis results
        if analysis_id:
            # Get specific analysis
            results = analysis_service.get_analysis_results(analysis_id, analysis_type)
            if not results:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Analysis results not found for analysis {analysis_id}"
                )
        else:
            # Get latest analysis
            analysis = analysis_service.get_latest_analysis(project_id, analysis_type)
            if not analysis:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No analysis found for project {project_id}"
                )
            
            results = analysis_service.get_analysis_results(analysis["id"], analysis_type)
            if not results:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Analysis results not found for analysis {analysis['id']}"
                )
        
        return results
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis results: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analysis results: {str(e)}"
        )