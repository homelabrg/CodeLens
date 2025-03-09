# services/source-code-service/app/database/projects.py
from typing import Dict, List, Optional, Any
from datetime import datetime
import os
import json
import logging
from ..core.config import settings

logger = logging.getLogger(__name__)

class ProjectDatabase:
    """
    Simple project database implementation using JSON files.
    
    For MVP phase, we'll use a file-based storage solution.
    This can be replaced with MongoDB or another database later.
    """
    
    def __init__(self):
        """Initialize the project database."""
        self.db_path = settings.DB_PATH
        os.makedirs(self.db_path, exist_ok=True)
        self.projects_file = os.path.join(self.db_path, "projects.json")
        
        # Create projects file if it doesn't exist
        if not os.path.exists(self.projects_file):
            with open(self.projects_file, "w") as f:
                json.dump({}, f)
    
    def _read_db(self) -> Dict[str, Any]:
        """Read the projects database file."""
        try:
            with open(self.projects_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error reading projects database: {str(e)}")
            return {}
    
    def _write_db(self, data: Dict[str, Any]) -> None:
        """Write data to the projects database file."""
        try:
            with open(self.projects_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error writing to projects database: {str(e)}")
    
    def create_project(self, project_info: Dict[str, Any]) -> bool:
        """
        Create a new project record.
        
        Args:
            project_info: Project information
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Read current data
            data = self._read_db()
            
            # Add new project
            project_id = project_info["id"]
            data[project_id] = project_info
            
            # Write updated data
            self._write_db(data)
            return True
        except Exception as e:
            logger.error(f"Error creating project record: {str(e)}")
            return False
    
    def update_project_status(self, project_id: str, status: str) -> bool:
        """
        Update the status of a project.
        
        Args:
            project_id: Project ID
            status: New status
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Read current data
            data = self._read_db()
            
            # Check if project exists
            if project_id not in data:
                return False
            
            # Update status and updated_at
            data[project_id]["status"] = status
            data[project_id]["updated_at"] = datetime.utcnow().isoformat()
            
            # Write updated data
            self._write_db(data)
            return True
        except Exception as e:
            logger.error(f"Error updating project status: {str(e)}")
            return False
    
    def update_project(self, project_id: str, **kwargs) -> bool:
        """
        Update project information.
        
        Args:
            project_id: Project ID
            **kwargs: Fields to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Read current data
            data = self._read_db()
            
            # Check if project exists
            if project_id not in data:
                return False
            
            # Update fields
            for key, value in kwargs.items():
                data[project_id][key] = value
            
            # Update updated_at
            data[project_id]["updated_at"] = datetime.utcnow().isoformat()
            
            # Write updated data
            self._write_db(data)
            return True
        except Exception as e:
            logger.error(f"Error updating project: {str(e)}")
            return False
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get project information.
        
        Args:
            project_id: Project ID
            
        Returns:
            Optional[Dict[str, Any]]: Project information or None if not found
        """
        try:
            # Read current data
            data = self._read_db()
            
            # Return project info if it exists
            return data.get(project_id)
        except Exception as e:
            logger.error(f"Error getting project: {str(e)}")
            return None
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """
        List all projects.
        
        Returns:
            List[Dict[str, Any]]: List of projects
        """
        try:
            # Read current data
            data = self._read_db()
            
            # Return list of projects
            return list(data.values())
        except Exception as e:
            logger.error(f"Error listing projects: {str(e)}")
            return []
    
    def delete_project(self, project_id: str) -> bool:
        """
        Delete a project record.
        
        Args:
            project_id: Project ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Read current data
            data = self._read_db()
            
            # Check if project exists
            if project_id not in data:
                return False
            
            # Delete project
            del data[project_id]
            
            # Write updated data
            self._write_db(data)
            return True
        except Exception as e:
            logger.error(f"Error deleting project: {str(e)}")
            return False