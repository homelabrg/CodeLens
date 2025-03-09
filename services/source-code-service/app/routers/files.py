# services/source-code-service/app/routers/files.py
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks, status
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import os
import uuid
import shutil
import logging
from pathlib import Path
import zipfile
import tempfile

from ..services.file_service import FileService
from ..dependencies.service_dependencies import get_file_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    project_name: str = Form(...),
    description: Optional[str] = Form(None),
    file_service: FileService = Depends(get_file_service)
):
    """
    Upload source code files for analysis.
    
    This endpoint accepts individual files or ZIP archives.
    For ZIP archives, the files will be extracted automatically.
    """
    try:
        # Generate a unique project ID
        project_id = str(uuid.uuid4())
        
        # Create initial record
        project_info = file_service.create_project(
            project_id=project_id,
            name=project_name,
            description=description,
            status="pending"
        )
        
        # Process files in the background
        background_tasks.add_task(
            file_service.process_uploaded_files,
            project_id=project_id,
            files=files
        )
        
        return {
            "project_id": project_id,
            "name": project_name,
            "status": "pending",
            "message": "Files are being processed. Check status using the project ID."
        }
        
    except Exception as e:
        logger.error(f"Failed to upload files: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload files: {str(e)}"
        )

@router.get("/projects/{project_id}")
async def get_project_status(
    project_id: str,
    file_service: FileService = Depends(get_file_service)
):
    """
    Get the status of a project.
    """
    try:
        project_info = file_service.get_project(project_id)
        if not project_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        return project_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get project status: {str(e)}"
        )

@router.get("/projects")
async def list_projects(
    file_service: FileService = Depends(get_file_service)
):
    """
    List all projects.
    """
    try:
        projects = file_service.list_projects()
        return projects
    except Exception as e:
        logger.error(f"Failed to list projects: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list projects: {str(e)}"
        )

@router.get("/projects/{project_id}/files")
async def list_project_files(
    project_id: str,
    file_service: FileService = Depends(get_file_service)
):
    """
    List all files in a project.
    """
    try:
        files = file_service.list_project_files(project_id)
        if files is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        return files
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list project files: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list project files: {str(e)}"
        )

@router.get("/projects/{project_id}/files/{file_path:path}")
async def get_file_content(
    project_id: str,
    file_path: str,
    file_service: FileService = Depends(get_file_service)
):
    """
    Get the content of a file in a project.
    """
    try:
        content = file_service.get_file_content(project_id, file_path)
        if content is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File {file_path} not found in project {project_id}"
            )
        return {
            "project_id": project_id,
            "file_path": file_path,
            "content": content
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get file content: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get file content: {str(e)}"
        )

@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: str,
    file_service: FileService = Depends(get_file_service)
):
    """
    Delete a project.
    """
    try:
        success = file_service.delete_project(project_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete project: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}"
        )