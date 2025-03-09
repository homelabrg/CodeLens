from typing import Dict, List, Optional, Any
from datetime import datetime
import os
import json
import logging
from ..core.config import settings

logger = logging.getLogger(__name__)

class RepositoryDatabase:
    """
    Simple repository database implementation using JSON files.
    
    This class provides persistence for repository information. We're using
    a file-based JSON store for simplicity in the MVP phase, which can be
    replaced with MongoDB or another database later.
    """
    
    def __init__(self):
        """Initialize the repository database."""
        self.db_path = settings.DB_PATH
        os.makedirs(self.db_path, exist_ok=True)
        self.repo_file = os.path.join(self.db_path, "repositories.json")
        
        # Create repositories file if it doesn't exist
        if not os.path.exists(self.repo_file):
            with open(self.repo_file, "w") as f:
                json.dump({}, f)
    
    def _read_db(self) -> Dict[str, Any]:
        """Read the repository database file."""
        try:
            with open(self.repo_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error reading repository database: {str(e)}")
            return {}
    
    def _write_db(self, data: Dict[str, Any]) -> None:
        """Write data to the repository database file."""
        try:
            with open(self.repo_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error writing to repository database: {str(e)}")
    
    def create_repository(self, repository_id: str, owner: str, repo: str, 
                          url: str, branch: str, status: str) -> bool:
        """
        Create a new repository record.
        
        Args:
            repository_id: Unique ID for the repository
            owner: Repository owner (GitHub username or organization)
            repo: Repository name
            url: Repository URL
            branch: Branch name
            status: Repository status (pending, cloning, ready, failed)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Read current data
            data = self._read_db()
            
            # Add new repository
            now = datetime.utcnow().isoformat()
            data[repository_id] = {
                "id": repository_id,
                "owner": owner,
                "repo": repo,
                "url": url,
                "branch": branch,
                "status": status,
                "file_count": None,
                "languages": None,
                "size_kb": None,
                "created_at": now,
                "updated_at": now
            }
            
            # Write updated data
            self._write_db(data)
            return True
        except Exception as e:
            logger.error(f"Error creating repository record: {str(e)}")
            return False
    
    def get_repository(self, repository_id: str) -> Optional[Dict[str, Any]]:
        """
        Get repository information.
        
        Args:
            repository_id: Repository ID
            
        Returns:
            Optional[Dict[str, Any]]: Repository information or None if not found
        """
        try:
            # Read current data
            data = self._read_db()
            
            # Return repository info if it exists
            return data.get(repository_id)
        except Exception as e:
            logger.error(f"Error getting repository: {str(e)}")
            return None

    def list_repositories(self) -> List[Dict[str, Any]]:
        """
        List all repositories.
        
        Returns:
            List[Dict[str, Any]]: List of repositories
        """
        try:
            # Read current data
            data = self._read_db()
            
            # Return list of repositories
            return list(data.values())
        except Exception as e:
            logger.error(f"Error listing repositories: {str(e)}")
            return []
        
    def update_repository_status(self, repository_id: str, status: str) -> bool:
        """Update the status of a repository."""
        try:
            # Read current data
            data = self._read_db()
            
            # Check if repository exists
            if repository_id not in data:
                return False
            
            # Update status and updated_at
            data[repository_id]["status"] = status
            data[repository_id]["updated_at"] = datetime.utcnow().isoformat()
            
            # Write updated data
            self._write_db(data)
            return True
        except Exception as e:
            logger.error(f"Error updating repository status: {str(e)}")
            return False
    
    def update_repository(self, repository_id: str, **kwargs) -> bool:
        """Update repository information."""
        try:
            # Read current data
            data = self._read_db()
            
            # Check if repository exists
            if repository_id not in data:
                return False
            
            # Update fields
            for key, value in kwargs.items():
                data[repository_id][key] = value
            
            # Update updated_at
            data[repository_id]["updated_at"] = datetime.utcnow().isoformat()
            
            # Write updated data
            self._write_db(data)
            return True
        except Exception as e:
            logger.error(f"Error updating repository: {str(e)}")
            return False