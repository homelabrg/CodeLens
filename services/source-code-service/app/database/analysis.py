# services/source-code-service/app/database/analysis.py
from typing import Dict, List, Optional, Any
from datetime import datetime
import os
import json
import logging
from ..core.config import settings

logger = logging.getLogger(__name__)

class AnalysisDatabase:
    """
    Simple analysis database implementation using JSON files.
    
    For MVP phase, we'll use a file-based storage solution.
    This can be replaced with MongoDB or another database later.
    """
    
    def __init__(self):
        """Initialize the analysis database."""
        self.db_path = settings.DB_PATH
        os.makedirs(self.db_path, exist_ok=True)
        self.analysis_file = os.path.join(self.db_path, "analysis.json")
        
        # Create analysis file if it doesn't exist
        if not os.path.exists(self.analysis_file):
            with open(self.analysis_file, "w") as f:
                json.dump({}, f)
    
    def _read_db(self) -> Dict[str, Any]:
        """Read the analysis database file."""
        try:
            with open(self.analysis_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error reading analysis database: {str(e)}")
            return {}
    
    def _write_db(self, data: Dict[str, Any]) -> None:
        """Write data to the analysis database file."""
        try:
            with open(self.analysis_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error writing to analysis database: {str(e)}")
    
    def create_analysis_job(self, analysis_info: Dict[str, Any]) -> bool:
        """
        Create a new analysis job record.
        
        Args:
            analysis_info: Analysis job information
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Read current data
            data = self._read_db()
            
            # Add new analysis
            analysis_id = analysis_info["id"]
            data[analysis_id] = analysis_info
            
            # Write updated data
            self._write_db(data)
            return True
        except Exception as e:
            logger.error(f"Error creating analysis job record: {str(e)}")
            return False
    
    def update_analysis_job(self, analysis_id: str, **kwargs) -> bool:
        """
        Update analysis job information.
        
        Args:
            analysis_id: Analysis job ID
            **kwargs: Fields to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Read current data
            data = self._read_db()
            
            # Check if analysis exists
            if analysis_id not in data:
                return False
            
            # Update fields
            for key, value in kwargs.items():
                data[analysis_id][key] = value
            
            # Update updated_at
            data[analysis_id]["updated_at"] = datetime.utcnow().isoformat()
            
            # Write updated data
            self._write_db(data)
            return True
        except Exception as e:
            logger.error(f"Error updating analysis job: {str(e)}")
            return False
    
    def get_analysis_job(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Get analysis job information.
        
        Args:
            analysis_id: Analysis job ID
            
        Returns:
            Optional[Dict[str, Any]]: Analysis job information or None if not found
        """
        try:
            # Read current data
            data = self._read_db()
            
            # Return analysis info if it exists
            return data.get(analysis_id)
        except Exception as e:
            logger.error(f"Error getting analysis job: {str(e)}")
            return None
    
    def list_analysis_jobs(self) -> List[Dict[str, Any]]:
        """
        List all analysis jobs.
        
        Returns:
            List[Dict[str, Any]]: List of analysis jobs
        """
        try:
            # Read current data
            data = self._read_db()
            
            # Return list of analyses
            return list(data.values())
        except Exception as e:
            logger.error(f"Error listing analysis jobs: {str(e)}")
            return []
    
    def list_project_analyses(self, project_id: str) -> List[Dict[str, Any]]:
        """
        List all analysis jobs for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            List[Dict[str, Any]]: List of analysis jobs for the project
        """
        try:
            # Read current data
            data = self._read_db()
            
            # Filter analyses by project ID
            project_analyses = [
                analysis for analysis in data.values()
                if analysis.get("project_id") == project_id
            ]
            
            return project_analyses
        except Exception as e:
            logger.error(f"Error listing project analyses: {str(e)}")
            return []
    
    def delete_analysis_job(self, analysis_id: str) -> bool:
        """
        Delete an analysis job record.
        
        Args:
            analysis_id: Analysis job ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Read current data
            data = self._read_db()
            
            # Check if analysis exists
            if analysis_id not in data:
                return False
            
            # Delete analysis
            del data[analysis_id]
            
            # Write updated data
            self._write_db(data)
            return True
        except Exception as e:
            logger.error(f"Error deleting analysis job: {str(e)}")
            return False