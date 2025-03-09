from ..database.analysis import AnalysisDatabase
from ..database.repositories import RepositoryDatabase
from ..database.projects import ProjectDatabase
from ..services.github_service import GitHubService
from ..services.openai_service import OpenAIService
from ..services.file_service import FileService

# Singleton instances
_repository_db = None
_project_db = None
_analysis_db = None
_github_service = None
_file_service = None
_openai_service = None
_analysis_service = None

def get_repository_db() -> RepositoryDatabase:
    """Get or create a RepositoryDatabase instance."""
    global _repository_db
    if _repository_db is None:
        _repository_db = RepositoryDatabase()
    return _repository_db

def get_project_db() -> ProjectDatabase:
    """Get or create a ProjectDatabase instance."""
    global _project_db
    if _project_db is None:
        _project_db = ProjectDatabase()
    return _project_db

def get_analysis_db() -> AnalysisDatabase:
    """Get or create an AnalysisDatabase instance."""
    global _analysis_db
    if _analysis_db is None:
        _analysis_db = AnalysisDatabase()
    return _analysis_db

def get_github_service() -> GitHubService:
    """Get or create a GitHubService instance."""
    global _github_service
    if _github_service is None:
        _github_service = GitHubService(get_repository_db())
    return _github_service

def get_file_service() -> FileService:
    """Get or create a FileService instance."""
    global _file_service
    if _file_service is None:
        _file_service = FileService(get_project_db())
    return _file_service

def get_openai_service() -> OpenAIService:
    """Get or create an OpenAIService instance."""
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService()
    return _openai_service

from ..services.analysis_service import AnalysisService
def get_analysis_service() -> AnalysisService:
    """Get or create an AnalysisService instance."""
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = AnalysisService(get_analysis_db(), get_openai_service(), get_file_service())
    return _analysis_service
