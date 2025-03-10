# services/source-code-service/app/utils/analysis_formatter.py
from typing import Dict, Any, Optional
from datetime import datetime
from ..models.analysis import (
    AnalysisResultsResponse,
    CodeAnalysisResponse,
    DependencyAnalysisResponse,
    BusinessAnalysisResponse,
    ArchitectureAnalysisResponse
)


def format_analysis_results(analysis_data: Dict[str, Any]) -> AnalysisResultsResponse:
    """
    Format raw analysis data into structured response model.
    
    Args:
        analysis_data: Raw analysis data from database
        
    Returns:
        AnalysisResultsResponse: Structured analysis results
    """
    # Convert string datetime to datetime objects if needed
    created_at = analysis_data.get("created_at")
    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at)
    
    updated_at = analysis_data.get("updated_at")
    if isinstance(updated_at, str):
        updated_at = datetime.fromisoformat(updated_at)
    
    completed_at = analysis_data.get("completed_at")
    if isinstance(completed_at, str):
        completed_at = datetime.fromisoformat(completed_at)
    
    # Initialize results
    results = {
        "id": analysis_data.get("id", ""),
        "project_id": analysis_data.get("project_id", ""),
        "status": analysis_data.get("status", "pending"),
        "analysis_types": analysis_data.get("analysis_types", []),
        "progress": analysis_data.get("progress", 0),
        "created_at": created_at,
        "updated_at": updated_at,
        "completed_at": completed_at,
        "project_name": analysis_data.get("project_name", ""),
        "file_count": analysis_data.get("file_count", 0),
        "languages": analysis_data.get("languages", []),
        "error": analysis_data.get("error")
    }
    
    # Extract analysis results if available
    raw_results = analysis_data.get("results", {})
    
    # Format code analysis results
    if "code" in raw_results:
        code_data = raw_results["code"]
        results["code"] = CodeAnalysisResponse(
            language_summaries=code_data.get("language_summaries", {}),
            file_summaries=code_data.get("file_summaries", {}),
            file_count=code_data.get("file_count", 0),
            language_distribution=code_data.get("language_distribution", {})
        )
    
    # Format dependency analysis results
    if "dependencies" in raw_results:
        dep_data = raw_results["dependencies"]
        results["dependencies"] = DependencyAnalysisResponse(
            dependencies=dep_data.get("dependencies", ""),
            dependency_graph=dep_data.get("dependency_graph", ""),
            analyzed_files=dep_data.get("analyzed_files", [])
        )
    
    # Format business analysis results
    if "business" in raw_results:
        bus_data = raw_results["business"]
        results["business"] = BusinessAnalysisResponse(
            business_functionality=bus_data.get("business_functionality", ""),
            business_entities=bus_data.get("business_entities", {}),
            analyzed_files=bus_data.get("analyzed_files", [])
        )
    
    # Format architecture analysis results
    if "architecture" in raw_results:
        arch_data = raw_results["architecture"]
        results["architecture"] = ArchitectureAnalysisResponse(
            architecture_analysis=arch_data.get("architecture_analysis", ""),
            architecture_diagram=arch_data.get("architecture_diagram", ""),
            analyzed_files=arch_data.get("analyzed_files", [])
        )
    
    return AnalysisResultsResponse(**results)


def extract_key_findings(analysis_results: AnalysisResultsResponse) -> Dict[str, Any]:
    """
    Extract key findings from analysis results for summary view.
    
    Args:
        analysis_results: Structured analysis results
        
    Returns:
        Dict[str, Any]: Key findings summary
    """
    findings = {
        "summary": {},
        "code": {},
        "dependencies": {},
        "business": {},
        "architecture": {}
    }
    
    # Project summary
    findings["summary"] = {
        "name": analysis_results.project_name,
        "file_count": analysis_results.file_count,
        "languages": analysis_results.languages,
        "analysis_date": analysis_results.completed_at
    }
    
    # Code findings
    if analysis_results.code:
        findings["code"] = {
            "language_count": len(analysis_results.code.language_distribution),
            "primary_language": _get_primary_language(analysis_results.code.language_distribution),
            "analyzed_files": len(analysis_results.code.file_summaries)
        }
    
    # Dependency findings
    if analysis_results.dependencies:
        findings["dependencies"] = {
            "analyzed_files": len(analysis_results.dependencies.analyzed_files)
        }
    
    # Business findings
    if analysis_results.business:
        findings["business"] = {
            "analyzed_files": len(analysis_results.business.analyzed_files)
        }
    
    # Architecture findings
    if analysis_results.architecture:
        findings["architecture"] = {
            "analyzed_files": len(analysis_results.architecture.analyzed_files)
        }
    
    return findings


def _get_primary_language(language_distribution: Dict[str, int]) -> str:
    """
    Get the primary language from distribution.
    
    Args:
        language_distribution: Distribution of languages
        
    Returns:
        str: Primary language or empty string if none
    """
    if not language_distribution:
        return ""
    
    # Find language with highest count
    return max(language_distribution.items(), key=lambda x: x[1])[0]