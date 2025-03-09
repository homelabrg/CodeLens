import os
import shutil
import logging
import uuid
from typing import Dict, List, Optional, Tuple, Any
import git
from urllib.parse import urlparse
from ..core.config import settings
from ..database.repositories import RepositoryDatabase

logger = logging.getLogger(__name__)

class GitHubService:
    """
    Service for interacting with GitHub repositories.
    
    This service handles cloning repositories, extracting information,
    and managing the repository lifecycle.
    """
    
    def __init__(self, repository_db: RepositoryDatabase):
        self.repository_db = repository_db
        self.clone_base_path = settings.CLONE_BASE_PATH
        
        # Ensure the clone directory exists
        os.makedirs(self.clone_base_path, exist_ok=True)
    
    def extract_owner_repo(self, repository_url: str) -> Tuple[str, str]:
        """
        Extract owner and repo name from GitHub URL.
        
        Args:
            repository_url: GitHub repository URL
            
        Returns:
            Tuple[str, str]: Owner and repository name
        """
        parsed_url = urlparse(repository_url)
        path_parts = parsed_url.path.strip('/').split('/')
        
        # Handle different GitHub URL formats
        if len(path_parts) >= 2:
            owner = path_parts[0]
            repo = path_parts[1].replace('.git', '')
            return owner, repo
        else:
            raise ValueError(f"Could not extract owner and repo from URL: {repository_url}")
    
    def start_clone(self, repository_url: str, branch: str = "main", 
                   access_token: Optional[str] = None) -> str:
        """
        Initialize repository cloning process and return a unique ID.
        
        Args:
            repository_url: GitHub repository URL
            branch: Branch to clone
            access_token: GitHub access token for private repositories
            
        Returns:
            str: Repository ID
        """
        repository_id = str(uuid.uuid4())
        
        # Extract owner and repo from URL
        owner, repo = self.extract_owner_repo(repository_url)
        
        # Create initial entry in database
        self.repository_db.create_repository(
            repository_id=repository_id,
            owner=owner,
            repo=repo,
            url=repository_url,
            branch=branch,
            status="pending"
        )
        
        return repository_id
    
    def clone_repository(self, repository_id: str, repository_url: str, 
                        branch: str = "main", access_token: Optional[str] = None) -> bool:
        """
        Clone a GitHub repository.
        
        Args:
            repository_id: Repository ID
            repository_url: GitHub repository URL
            branch: Branch to clone
            access_token: GitHub access token for private repositories
            
        Returns:
            bool: True if successful, False otherwise
        """
        clone_path = os.path.join(self.clone_base_path, repository_id)
        
        try:
            # Update repository status to "cloning"
            self.repository_db.update_repository_status(repository_id, "cloning")
            
            # Format URL with access token if provided
            if access_token:
                if "github.com" in repository_url:
                    url_parts = repository_url.split("//")
                    clone_url = f"{url_parts[0]}//{access_token}@{url_parts[1]}"
                else:
                    clone_url = repository_url
            else:
                clone_url = repository_url
            
            # Create directory for cloning
            os.makedirs(clone_path, exist_ok=True)
            
            # Clone the repository
            logger.info(f"Cloning repository: {repository_url} (branch: {branch}) to {clone_path}")
            
            repo = git.Repo.clone_from(
                clone_url, 
                clone_path,
                branch=branch,
                depth=1  # Shallow clone to save space and time
            )
            
            # Get repository information
            file_count = sum(1 for _ in repo.git.ls_files().splitlines())
            languages = self._detect_languages(clone_path)
            size_kb = self._get_directory_size(clone_path) // 1024
            
            # Update repository information in database
            self.repository_db.update_repository(
                repository_id=repository_id,
                status="ready",
                file_count=file_count,
                languages=languages,
                size_kb=size_kb
            )
            
            logger.info(f"Repository cloned successfully: {repository_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clone repository: {str(e)}", exc_info=True)
            # Update repository status to "failed"
            self.repository_db.update_repository_status(repository_id, "failed")
            
            # Clean up clone directory if it exists
            if os.path.exists(clone_path):
                shutil.rmtree(clone_path, ignore_errors=True)
                
            return False
            
    # Helper methods for language detection and directory size calculation
    def _detect_languages(self, directory_path: str) -> List[str]:
        """
        Detect programming languages used in the repository.
        
        Args:
            directory_path: Path to the repository directory
            
        Returns:
            List[str]: List of detected programming languages
        """
        languages = set()
        extension_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cs': 'C#',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rb': 'Ruby',
            '.php': 'PHP',
            # Add more languages as needed
        }
        
        for root, _, files in os.walk(directory_path):
            for file in files:
                _, ext = os.path.splitext(file)
                if ext in extension_map:
                    languages.add(extension_map[ext])
        
        return list(languages)
    
    def _get_directory_size(self, directory_path: str) -> int:
        """
        Get the size of a directory in bytes.
        
        Args:
            directory_path: Path to the directory
            
        Returns:
            int: Directory size in bytes
        """
        total_size = 0
        for dirpath, _, filenames in os.walk(directory_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if os.path.isfile(file_path):
                    total_size += os.path.getsize(file_path)
        
        return total_size
    
    def get_repository_info(self, repository_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a cloned repository.
        
        Args:
            repository_id: Repository ID
                
        Returns:
            Optional[Dict[str, Any]]: Repository information or None if not found
        """
        return self.repository_db.get_repository(repository_id)
    
    def list_repositories(self) -> List[Dict[str, Any]]:
        """
        List all repositories that have been cloned.
        
        Returns:
            List[Dict[str, Any]]: List of repositories
        """
        return self.repository_db.list_repositories()
