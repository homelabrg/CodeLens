# services/source-code-service/app/services/file_service.py
import os
import shutil
import logging
import uuid
import zipfile
import tempfile
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import UploadFile
from pathlib import Path

from ..core.config import settings
from ..database.projects import ProjectDatabase
from ..utils.language_detection import detect_language

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self, project_db: ProjectDatabase):
        self.project_db = project_db
        self.files_base_path = settings.FILES_BASE_PATH
        
        # Ensure the files directory exists
        os.makedirs(self.files_base_path, exist_ok=True)
    
    def create_project(self, project_id: str, name: str, description: Optional[str] = None, status: str = "pending") -> Dict[str, Any]:
        """
        Create a new project record.
        
        Args:
            project_id: Unique ID for the project
            name: Project name
            description: Project description
            status: Project status
            
        Returns:
            Dict: Project information
        """
        project_dir = os.path.join(self.files_base_path, project_id)
        os.makedirs(project_dir, exist_ok=True)
        
        project_info = {
            "id": project_id,
            "name": name,
            "description": description,
            "status": status,
            "file_count": 0,
            "languages": [],
            "size_kb": 0,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Save project information
        self.project_db.create_project(project_info)
        
        return project_info
    
    async def process_uploaded_files(self, project_id: str, files: List[UploadFile]):
        """
        Process uploaded files.
        
        Args:
            project_id: Project ID
            files: List of uploaded files
        """
        try:
            # Update project status
            self.project_db.update_project_status(project_id, "processing")
            
            project_dir = os.path.join(self.files_base_path, project_id)
            os.makedirs(project_dir, exist_ok=True)
            
            file_count = 0
            total_size = 0
            all_languages = set()
            file_list = []
            
            # Process each file
            for file in files:
                file_path = os.path.join(project_dir, file.filename)
                
                # Check if file is a ZIP archive
                if file.filename.endswith('.zip'):
                    # Create a temporary directory
                    with tempfile.TemporaryDirectory() as temp_dir:
                        # Save ZIP file
                        temp_zip = os.path.join(temp_dir, file.filename)
                        with open(temp_zip, "wb") as f:
                            shutil.copyfileobj(file.file, f)
                        
                        # Extract ZIP file
                        with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                            zip_ref.extractall(project_dir)
                        
                        # Process extracted files
                        extracted_data = self._process_directory(project_dir)
                        file_count += extracted_data["file_count"]
                        total_size += extracted_data["size_bytes"]
                        all_languages.update(extracted_data["languages"])
                        file_list.extend(extracted_data["files"])
                else:
                    # Save regular file
                    with open(file_path, "wb") as f:
                        shutil.copyfileobj(file.file, f)
                    
                    # Get file size
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    file_count += 1
                    
                    # Detect language
                    language = detect_language(file_path)
                    if language:
                        all_languages.add(language)
                    
                    # Add to file list
                    file_list.append({
                        "path": file.filename,
                        "size_bytes": file_size,
                        "language": language
                    })
            
            # Update project information
            self.project_db.update_project(
                project_id=project_id,
                status="ready",
                file_count=file_count,
                languages=list(all_languages),
                size_kb=total_size // 1024,
                files=file_list
            )
            
            logger.info(f"Successfully processed {file_count} files for project {project_id}")
            
        except Exception as e:
            logger.error(f"Failed to process files for project {project_id}: {str(e)}", exc_info=True)
            self.project_db.update_project_status(project_id, "failed")
    
    def _process_directory(self, directory_path: str) -> Dict[str, Any]:
        """
        Process a directory and gather information about its files.
        
        Args:
            directory_path: Path to the directory
            
        Returns:
            Dict: Information about the directory
        """
        file_count = 0
        total_size = 0
        languages = set()
        files = []
        
        for root, _, filenames in os.walk(directory_path):
            for filename in filenames:
                # Skip hidden files and directories
                if filename.startswith('.') or '/.git/' in root:
                    continue
                
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, directory_path)
                
                # Get file size
                file_size = os.path.getsize(file_path)
                total_size += file_size
                file_count += 1
                
                # Detect language
                language = detect_language(file_path)
                if language:
                    languages.add(language)
                
                # Add to file list
                files.append({
                    "path": relative_path,
                    "size_bytes": file_size,
                    "language": language
                })
        
        return {
            "file_count": file_count,
            "size_bytes": total_size,
            "languages": list(languages),
            "files": files
        }
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get project information.
        
        Args:
            project_id: Project ID
            
        Returns:
            Optional[Dict[str, Any]]: Project information or None if not found
        """
        return self.project_db.get_project(project_id)
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """
        List all projects.
        
        Returns:
            List[Dict[str, Any]]: List of projects
        """
        return self.project_db.list_projects()
    
    def list_project_files(self, project_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        List all files in a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Optional[List[Dict[str, Any]]]: List of files or None if project not found
        """
        project = self.project_db.get_project(project_id)
        if not project:
            return None
        
        return project.get("files", [])
    
    def get_file_content(self, project_id: str, file_path: str) -> Optional[str]:
        """
        Get the content of a file in a project.
        
        Args:
            project_id: Project ID
            file_path: Relative path to the file
            
        Returns:
            Optional[str]: File content or None if not found
        """
        project_dir = os.path.join(self.files_base_path, project_id)
        absolute_path = os.path.normpath(os.path.join(project_dir, file_path))
        
        # Security check: make sure the file is within the project directory
        if not absolute_path.startswith(project_dir):
            logger.warning(f"Attempted path traversal: {file_path}")
            return None
        
        # Check if file exists
        if not os.path.isfile(absolute_path):
            return None
        
        # Read file content
        try:
            with open(absolute_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with latin-1 encoding if utf-8 fails
            try:
                with open(absolute_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Failed to read file {absolute_path}: {str(e)}")
                return None
        except Exception as e:
            logger.error(f"Failed to read file {absolute_path}: {str(e)}")
            return None
    
    def delete_project(self, project_id: str) -> bool:
        """
        Delete a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Check if project exists
        project = self.project_db.get_project(project_id)
        if not project:
            return False
        
        # Delete project directory
        project_dir = os.path.join(self.files_base_path, project_id)
        if os.path.exists(project_dir):
            shutil.rmtree(project_dir, ignore_errors=True)
        
        # Delete project from database
        self.project_db.delete_project(project_id)
        
        return True
    
    def import_from_repository(self, repository_id: str, owner: str, repo: str) -> str:
        """
        Import files from a cloned repository to the file service.
        
        Args:
            repository_id: Repository ID
            owner: Repository owner
            repo: Repository name
            
        Returns:
            str: Project ID for the imported files
        """
        try:
            # Create a new project
            project_id = str(uuid.uuid4())
            project_name = f"{owner}/{repo}"
            description = f"Imported from GitHub repository {owner}/{repo}"
            
            # Create project entry
            self.create_project(
                project_id=project_id,
                name=project_name,
                description=description,
                status="importing"
            )
            
            # Get the repository path
            repo_path = os.path.join(settings.CLONE_BASE_PATH, repository_id)
            
            if not os.path.exists(repo_path):
                logger.error(f"Repository directory not found: {repo_path}")
                self.project_db.update_project_status(project_id, "failed")
                return None
            
            # Create project directory
            project_dir = os.path.join(self.files_base_path, project_id)
            os.makedirs(project_dir, exist_ok=True)
            
            # Copy files from repository to project
            file_count = 0
            total_size = 0
            all_languages = set()
            file_list = []
            
            # Process directory
            for root, _, files in os.walk(repo_path):
                # Skip hidden directories and files
                if "/." in root or "/.git/" in root:
                    continue
                    
                for filename in files:
                    # Skip hidden files
                    if filename.startswith('.'):
                        continue
                        
                    # Get source and destination paths
                    source_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(source_path, repo_path)
                    dest_path = os.path.join(project_dir, rel_path)
                    
                    # Create directories if needed
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    
                    # Copy the file
                    shutil.copy2(source_path, dest_path)
                    
                    # Get file size
                    file_size = os.path.getsize(dest_path)
                    total_size += file_size
                    file_count += 1
                    
                    # Detect language
                    from ..utils.language_detection import detect_language
                    language = detect_language(dest_path)
                    if language:
                        all_languages.add(language)
                    
                    # Add to file list
                    file_list.append({
                        "path": rel_path,
                        "size_bytes": file_size,
                        "language": language
                    })
            
            # Update project information
            self.project_db.update_project(
                project_id=project_id,
                status="ready",
                file_count=file_count,
                languages=list(all_languages),
                size_kb=total_size // 1024,
                files=file_list
            )
            
            logger.info(f"Successfully imported {file_count} files from repository {owner}/{repo}")
            
            return project_id
            
        except Exception as e:
            logger.error(f"Failed to import repository: {str(e)}", exc_info=True)
            if 'project_id' in locals():
                self.project_db.update_project_status(project_id, "failed")
            return None


    def process_project_files(self, project_id: str) -> bool:
        """
        Process files in a project to update project metadata.
        
        Args:
            project_id: Project ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            project_dir = os.path.join(self.files_base_path, project_id)
            if not os.path.exists(project_dir):
                logger.error(f"Project directory not found: {project_dir}")
                return False
            
            # Process files
            file_count = 0
            total_size = 0
            languages = set()
            files = []
            
            for root, _, filenames in os.walk(project_dir):
                for filename in filenames:
                    # Skip hidden files
                    if filename.startswith('.'):
                        continue
                    
                    file_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(file_path, project_dir)
                    
                    # Get file size
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    file_count += 1
                    
                    # Detect language
                    from ..utils.language_detection import detect_language
                    language = detect_language(file_path)
                    if language:
                        languages.add(language)
                    
                    # Add to files list
                    files.append({
                        "path": relative_path,
                        "size_bytes": file_size,
                        "language": language
                    })
            
            # Update project information
            self.project_db.update_project(
                project_id=project_id,
                status="ready",
                file_count=file_count,
                languages=list(languages),
                size_kb=total_size // 1024,
                files=files
            )
            
            logger.info(f"Processed {file_count} files in project {project_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to process project files: {str(e)}", exc_info=True)
            self.project_db.update_project_status(project_id, "failed")
            return False