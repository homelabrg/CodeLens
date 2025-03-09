import os
import logging
import uuid
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import asyncio

from ..core.config import settings
from ..database.analysis import AnalysisDatabase
from .openai_service import OpenAIService
from .file_service import FileService
from ..services.github_service import GitHubService
# from ..dependencies.service_dependencies import get_github_service
logger = logging.getLogger(__name__)

class AnalysisService:
    def __init__(self, 
                 analysis_db: AnalysisDatabase, 
                 openai_service: OpenAIService,
                 file_service: FileService):
        self.analysis_db = analysis_db
        self.openai_service = openai_service
        self.file_service = file_service
        self.analysis_results_path = settings.ANALYSIS_RESULTS_PATH
        
        # Ensure the results directory exists
        os.makedirs(self.analysis_results_path, exist_ok=True)
    
    def create_analysis_job(self, project_id: str, analysis_types: List[str], project_info: Dict[str, Any]) -> str:
        """
        Create a new analysis job.
        
        Args:
            project_id: Project ID
            analysis_types: Types of analysis to perform
            project_info: Project information
            
        Returns:
            str: Analysis job ID
        """
        analysis_id = str(uuid.uuid4())
        
        # Create analysis job record
        analysis_info = {
            "id": analysis_id,
            "project_id": project_id,
            "analysis_types": analysis_types,
            "status": "pending",
            "progress": 0,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "results": {},
            "error": None
        }
        
        # Add project metadata
        analysis_info["project_name"] = project_info.get("name", "")
        analysis_info["file_count"] = project_info.get("file_count", 0)
        analysis_info["languages"] = project_info.get("languages", [])
        
        # Save analysis job
        self.analysis_db.create_analysis_job(analysis_info)
        
        return analysis_id
    
    async def run_analysis(self, analysis_id: str, project_id: str, analysis_types: List[str]):
        """
        Run analysis job.
        
        Args:
            analysis_id: Analysis job ID
            project_id: Project ID
            analysis_types: Types of analysis to perform
        """
        try:
            # Update job status
            self.analysis_db.update_analysis_job(analysis_id, status="running", progress=0)
            
            # Get project information
            project = self.file_service.get_project(project_id)
            if not project:
                self.analysis_db.update_analysis_job(
                    analysis_id, 
                    status="failed", 
                    error=f"Project with ID {project_id} not found"
                )
                return
            
            # Get project files
            files = self.file_service.list_project_files(project_id)
            if not files:
                self.analysis_db.update_analysis_job(
                    analysis_id, 
                    status="failed", 
                    error=f"No files found for project {project_id}"
                )
                return
            
            # Determine total analysis tasks
            total_tasks = len(analysis_types)
            completed_tasks = 0
            results = {}
            
            # Perform each analysis type
            for analysis_type in analysis_types:
                # Update progress
                progress = int((completed_tasks / total_tasks) * 100)
                self.analysis_db.update_analysis_job(analysis_id, progress=progress)
                
                try:
                    # Perform analysis based on type
                    if analysis_type == "code":
                        result = await self._analyze_code(project_id, files)
                    elif analysis_type == "dependencies":
                        result = await self._analyze_dependencies(project_id, files)
                    elif analysis_type == "business":
                        result = await self._analyze_business(project_id, files)
                    elif analysis_type == "architecture":
                        result = await self._analyze_architecture(project_id, files)
                    else:
                        logger.warning(f"Unknown analysis type: {analysis_type}")
                        continue
                    
                    # Store results 
                    results[analysis_type] = result
                    
                    # Save results to file
                    self._save_analysis_results(analysis_id, analysis_type, result)
                    
                except Exception as e:
                    logger.error(f"Error performing {analysis_type} analysis: {str(e)}", exc_info=True)
                    results[analysis_type] = {"error": str(e)}
                
                # Increment completed tasks
                completed_tasks += 1
            
            # Update job with results
            self.analysis_db.update_analysis_job(
                analysis_id,
                status="completed",
                progress=100,
                results=results,
                completed_at=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error running analysis job: {str(e)}", exc_info=True)
            self.analysis_db.update_analysis_job(
                analysis_id,
                status="failed",
                error=str(e)
            )
    
    async def _analyze_code(self, project_id: str, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze code files.
        
        Args:
            project_id: Project ID
            files: List of files
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        logger.info(f"Starting code analysis for project {project_id}")
        
        # Filter to only code files
        code_files = [f for f in files if f.get("language") is not None]
        
        # Group files by language
        language_files = {}
        for file in code_files:
            lang = file.get("language")
            if lang:
                if lang not in language_files:
                    language_files[lang] = []
                language_files[lang].append(file)
        
        # Analyze files by language
        language_summaries = {}
        file_summaries = {}
        
        # Process each language
        for language, lang_files in language_files.items():
            # Get language summary
            prompt = self._create_language_summary_prompt(language, lang_files)
            language_summary = await self.openai_service.analyze_text(prompt)
            language_summaries[language] = language_summary
            
            # Process a sample of files for each language (up to 10)
            sample_files = lang_files[:10]
            for file_info in sample_files:
                file_path = file_info.get("path")
                if file_path:
                    file_content = self.file_service.get_file_content(project_id, file_path)
                    if file_content:
                        # Get file summary
                        prompt = self._create_file_summary_prompt(file_path, language, file_content)
                        file_summary = await self.openai_service.analyze_text(prompt)
                        file_summaries[file_path] = file_summary
        
        return {
            "language_summaries": language_summaries,
            "file_summaries": file_summaries,
            "file_count": len(code_files),
            "language_distribution": {lang: len(files) for lang, files in language_files.items()}
        }
    
    async def _analyze_dependencies(self, project_id: str, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze dependencies between code files.
        
        Args:
            project_id: Project ID
            files: List of files
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        logger.info(f"Starting dependency analysis for project {project_id}")
        
        # Filter to only code files
        code_files = [f for f in files if f.get("language") is not None]
        
        # Sample files for analysis (up to 20)
        sample_files = code_files[:20]
        
        # Collect file contents
        file_contents = {}
        for file_info in sample_files:
            file_path = file_info.get("path")
            if file_path:
                content = self.file_service.get_file_content(project_id, file_path)
                if content:
                    file_contents[file_path] = content
        
        # Analyze dependencies
        prompt = self._create_dependency_analysis_prompt(file_contents)
        dependency_analysis = await self.openai_service.analyze_text(prompt)
        
        # Generate dependency graph
        graph_prompt = self._create_dependency_graph_prompt(dependency_analysis)
        dependency_graph = await self.openai_service.analyze_text(graph_prompt)
        
        return {
            "dependencies": dependency_analysis,
            "dependency_graph": dependency_graph,
            "analyzed_files": list(file_contents.keys())
        }
    
    async def _analyze_business(self, project_id: str, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze business functionality.
        
        Args:
            project_id: Project ID
            files: List of files
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        logger.info(f"Starting business functionality analysis for project {project_id}")
        
        # Filter to only code files
        code_files = [f for f in files if f.get("language") is not None]
        
        # Sample files for analysis (up to 20)
        sample_files = code_files[:20]
        
        # Collect file contents
        file_contents = {}
        for file_info in sample_files:
            file_path = file_info.get("path")
            if file_path:
                content = self.file_service.get_file_content(project_id, file_path)
                if content:
                    file_contents[file_path] = content
        
        # Analyze business functionality
        prompt = self._create_business_analysis_prompt(file_contents)
        business_analysis = await self.openai_service.analyze_text(prompt)
        
        # Extract business entities
        entity_prompt = self._create_business_entity_prompt(business_analysis)
        business_entities = await self.openai_service.analyze_text(entity_prompt)
        
        return {
            "business_functionality": business_analysis,
            "business_entities": business_entities,
            "analyzed_files": list(file_contents.keys())
        }
    
    async def _analyze_architecture(self, project_id: str, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze architecture.
        
        Args:
            project_id: Project ID
            files: List of files
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        logger.info(f"Starting architecture analysis for project {project_id}")
        
        # Get project information
        project = self.file_service.get_project(project_id)
        
        # Filter to only code files
        code_files = [f for f in files if f.get("language") is not None]
        
        # Sample files for analysis (up to 20)
        sample_files = code_files[:20]
        
        # Collect file contents
        file_contents = {}
        for file_info in sample_files:
            file_path = file_info.get("path")
            if file_path:
                content = self.file_service.get_file_content(project_id, file_path)
                if content:
                    file_contents[file_path] = content
        
        # Analyze architecture
        prompt = self._create_architecture_analysis_prompt(project, file_contents)
        architecture_analysis = await self.openai_service.analyze_text(prompt)
        
        # Generate architecture diagram
        diagram_prompt = self._create_architecture_diagram_prompt(architecture_analysis)
        architecture_diagram = await self.openai_service.analyze_text(diagram_prompt)
        
        return {
            "architecture_analysis": architecture_analysis,
            "architecture_diagram": architecture_diagram,
            "analyzed_files": list(file_contents.keys())
        }
    
    def _save_analysis_results(self, analysis_id: str, analysis_type: str, results: Dict[str, Any]):
        """
        Save analysis results to file.
        
        Args:
            analysis_id: Analysis job ID
            analysis_type: Type of analysis
            results: Analysis results
        """
        # Create directory for analysis results
        analysis_dir = os.path.join(self.analysis_results_path, analysis_id)
        os.makedirs(analysis_dir, exist_ok=True)
        
        # Save results to file
        results_file = os.path.join(analysis_dir, f"{analysis_type}.json")
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
    
    def get_analysis_job(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Get analysis job.
        
        Args:
            analysis_id: Analysis job ID
            
        Returns:
            Optional[Dict[str, Any]]: Analysis job information
        """
        return self.analysis_db.get_analysis_job(analysis_id)
    
    def list_project_analyses(self, project_id: str) -> List[Dict[str, Any]]:
        """
        List all analysis jobs for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            List[Dict[str, Any]]: List of analysis jobs
        """
        return self.analysis_db.list_project_analyses(project_id)
    
    def get_latest_analysis(self, project_id: str, analysis_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get the latest analysis for a project.
        
        Args:
            project_id: Project ID
            analysis_type: Type of analysis (optional)
            
        Returns:
            Optional[Dict[str, Any]]: Analysis job information
        """
        analyses = self.analysis_db.list_project_analyses(project_id)
        
        # Filter completed analyses
        completed_analyses = [a for a in analyses if a.get("status") == "completed"]
        
        if not completed_analyses:
            return None
        
        # Sort by created_at (descending)
        sorted_analyses = sorted(
            completed_analyses,
            key=lambda a: a.get("created_at", ""),
            reverse=True
        )
        
        # Filter by analysis type if specified
        if analysis_type:
            filtered_analyses = [
                a for a in sorted_analyses 
                if analysis_type in a.get("analysis_types", []) and 
                analysis_type in a.get("results", {})
            ]
            
            if not filtered_analyses:
                return None
            
            return filtered_analyses[0]
        
        return sorted_analyses[0] if sorted_analyses else None
    
    def get_analysis_results(self, analysis_id: str, analysis_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get analysis results.
        
        Args:
            analysis_id: Analysis job ID
            analysis_type: Type of analysis (optional)
            
        Returns:
            Optional[Dict[str, Any]]: Analysis results
        """
        # Get analysis job
        analysis = self.analysis_db.get_analysis_job(analysis_id)
        if not analysis:
            return None
        
        # If specific analysis type requested
        if analysis_type:
            # Check if results exist in database
            if analysis_type in analysis.get("results", {}):
                return analysis["results"][analysis_type]
            
            # Check if results exist in file
            results_file = os.path.join(self.analysis_results_path, analysis_id, f"{analysis_type}.json")
            if os.path.exists(results_file):
                try:
                    with open(results_file, "r") as f:
                        return json.load(f)
                except Exception as e:
                    logger.error(f"Error reading analysis results file: {str(e)}")
                    return None
            
            return None
        
        # Return all results
        results = {}
        
        # Get results from database
        db_results = analysis.get("results", {})
        results.update(db_results)
        
        # Get results from files
        results_dir = os.path.join(self.analysis_results_path, analysis_id)
        if os.path.exists(results_dir):
            for file_name in os.listdir(results_dir):
                if file_name.endswith(".json"):
                    analysis_type = file_name[:-5]  # Remove .json extension
                    if analysis_type not in results:
                        try:
                            with open(os.path.join(results_dir, file_name), "r") as f:
                                results[analysis_type] = json.load(f)
                        except Exception as e:
                            logger.error(f"Error reading analysis results file: {str(e)}")
        
        return results
    
    # Prompt generation methods
    def _create_language_summary_prompt(self, language: str, files: List[Dict[str, Any]]) -> str:
        """
        Create prompt for language summary.
        
        Args:
            language: Programming language
            files: List of files in the language
            
        Returns:
            str: Prompt for language summary
        """
        file_paths = [f.get("path", "") for f in files]
        file_list = "\n".join([f"- {path}" for path in file_paths[:20]])
        
        return f"""
You are a expert code analyzer specialized in {language}.

I have a codebase with {len(files)} files written in {language}. Here's a sample of the file paths:

{file_list}

Please provide a summary of what you can infer about this codebase based on the file structure and naming conventions.
Your analysis should cover:

1. The likely type of application or project (web app, library, command-line tool, etc.)
2. Potential architecture patterns that might be used
3. Possible frameworks or major dependencies based on directory structure
4. Any other insights you can provide about the codebase organization

Respond with a concise, professional summary. Do not make excessive assumptions beyond what the file structure suggests.
"""

    def _create_file_summary_prompt(self, file_path: str, language: str, content: str) -> str:
        """
        Create prompt for file summary.
        
        Args:
            file_path: File path
            language: Programming language
            content: File content
            
        Returns:
            str: Prompt for file summary
        """
        return f"""
You are a expert code analyzer specialized in {language}.

Please analyze the following code file:

File: {file_path}
Language: {language}

```{language}
{content[:7000]}  # Limit content to prevent token limits
```

Provide a concise summary of this file that includes:

1. The main purpose of this file
2. Key functions, classes, or components defined
3. Dependencies and imports
4. Notable patterns or techniques used
5. Any potential issues or code quality concerns

Keep your response brief but informative, focusing on the most important aspects of the code.
"""

    def _create_dependency_analysis_prompt(self, file_contents: Dict[str, str]) -> str:
        """
        Create prompt for dependency analysis.
        
        Args:
            file_contents: Dictionary of file paths and contents
            
        Returns:
            str: Prompt for dependency analysis
        """
        file_list = "\n".join([f"- {path}" for path in file_contents.keys()])
        
        # Create a sample of each file (first 100 lines)
        file_samples = []
        for path, content in file_contents.items():
            lines = content.split("\n")[:100]
            sample = "\n".join(lines)
            file_samples.append(f"File: {path}\n```\n{sample}\n```\n")
        
        file_samples_text = "\n".join(file_samples)
        
        return f"""
You are an expert business analyst who understands software code.

I have a codebase with the following files:

{file_list}

I'll provide samples of each file. Please analyze these files and identify:

1. The core business domain and functionality this code implements
2. Business processes and workflows represented in the code
3. Business rules and constraints embedded in the code
4. Business entities and their relationships
5. Business terminology used in the code

Here are the file samples:

{file_samples_text}

Provide a comprehensive analysis of the business functionality represented in this codebase, using business-oriented language rather than technical jargon where possible.
"""

    def _create_business_entity_prompt(self, business_analysis: str) -> str:
        """
        Create prompt for business entity extraction.
        
        Args:
            business_analysis: Business analysis results
            
        Returns:
            str: Prompt for business entity extraction
        """
        return f"""
You are an expert at extracting business domain models from code.

Based on the following business analysis, identify and describe the key business entities in this codebase and their relationships.

Business Analysis:
{business_analysis}

For each business entity:
1. Provide the entity name
2. Describe its purpose and meaning in the business domain
3. List its key attributes
4. Describe its relationships with other entities

Then, create a JSON representation of these entities and their relationships that could be used to generate an entity relationship diagram.

The JSON should be in the following format:
```json
{{
  "entities": [
    {{
      "name": "EntityName",
      "description": "Entity description",
      "attributes": ["attribute1", "attribute2"],
      "relationships": [
        {{
          "entity": "RelatedEntityName",
          "type": "one-to-many",
          "description": "Relationship description"
        }}
      ]
    }}
  ]
}}
```
"""

    def _create_architecture_analysis_prompt(self, project: Dict[str, Any], file_contents: Dict[str, str]) -> str:
        """
        Create prompt for architecture analysis.
        
        Args:
            project: Project information
            file_contents: Dictionary of file paths and contents
            
        Returns:
            str: Prompt for architecture analysis
        """
        project_name = project.get("name", "")
        languages = project.get("languages", [])
        file_list = "\n".join([f"- {path}" for path in file_contents.keys()])
        
        # Create a sample of each file (first 100 lines)
        file_samples = []
        for path, content in file_contents.items():
            lines = content.split("\n")[:100]
            sample = "\n".join(lines)
            file_samples.append(f"File: {path}\n```\n{sample}\n```\n")
        
        file_samples_text = "\n".join(file_samples)
        
        return f"""
You are an expert software architect specializing in {', '.join(languages)}.

I have a codebase named "{project_name}" with the following files:

{file_list}

I'll provide samples of each file. Please analyze these files and identify:

1. The overall architectural pattern(s) used in this codebase
2. Major components and their responsibilities
3. Component interactions and data flow
4. Technologies, frameworks, and libraries used
5. Architectural strengths and potential improvements

Here are the file samples:

{file_samples_text}

Provide a comprehensive architectural analysis of this codebase. Use standard architectural terminology and concepts.
"""

    def _create_architecture_diagram_prompt(self, architecture_analysis: str) -> str:
        """
        Create prompt for architecture diagram generation.
        
        Args:
            architecture_analysis: Architecture analysis results
            
        Returns:
            str: Prompt for architecture diagram generation
        """
        return f"""
You are an expert at creating software architecture diagrams.

Based on the following architectural analysis, create a Mermaid diagram representation of the architecture of this codebase.

Architectural Analysis:
{architecture_analysis}

Please generate a mermaid diagram definition using the following syntax:
```mermaid
graph TD
  subgraph Component1
    A[Module A]
    B[Module B]
  end
  subgraph Component2
    C[Module C]
    D[Module D]
  end
  A --> C
  B --> D
  // Add more relationships
```

Focus on the high-level architecture, major components, and their interactions. Use clear labels and organize the diagram for readability.
"""
        file_samples = []
        for path, content in file_contents.items():
            lines = content.split("\n")[:100]
            sample = "\n".join(lines)
            file_samples.append(f"File: {path}\n```\n{sample}\n```\n")
        
        file_samples_text = "\n".join(file_samples)
        
        return f"""
You are a expert dependency analyzer for software projects.

I have a codebase with the following files:

{file_list}

I'll provide samples of each file. Please analyze these files and identify:

1. Dependencies between files (imports, references)
2. Hierarchical relationships between components
3. Key modules and their responsibilities
4. Potential dependency issues (circular dependencies, tight coupling)

Here are the file samples:

{file_samples_text}

Provide a comprehensive analysis of the dependencies in this codebase based on the available information.
"""

    def _create_dependency_graph_prompt(self, dependency_analysis: str) -> str:
        """
        Create prompt for dependency graph generation.
        
        Args:
            dependency_analysis: Dependency analysis results
            
        Returns:
            str: Prompt for dependency graph generation
        """
        return f"""
You are a expert at creating visualizations of code dependencies.

Based on the following dependency analysis, create a Mermaid graph representation of the dependencies between components in the codebase.

Dependency Analysis:
{dependency_analysis}

Please generate a mermaid graph definition using the following syntax:
```mermaid
graph TD
  A[Component A] --> B[Component B]
  B --> C[Component C]
  // Add more dependencies
```

Focus on the most important components and relationships. Use clear labels and organize the graph for readability.
"""

    def _create_business_analysis_prompt(self, file_contents: Dict[str, str]) -> str:
        """
        Create prompt for business functionality analysis.
        
        Args:
            file_contents: Dictionary of file paths and contents
            
        Returns:
            str: Prompt for business functionality analysis
        """
        file_list = "\n".join([f"- {path}" for path in file_contents.keys()])
        
        # Create a sample of each file (first 100 lines
        
    
    
    def create_analysis_job(self, project_id: str, analysis_types: List[str], 
                            import_from_repository: bool = False) -> str:
        """
        Create a new analysis job.
        
        Args:
            project_id: Project ID or Repository ID (if import_from_repository is True)
            analysis_types: Types of analysis to perform
            import_from_repository: Whether to import files from a repository
            
        Returns:
            str: Analysis job ID
        """
        analysis_id = str(uuid.uuid4())
        
        try:
            if import_from_repository:
                # This is a repository ID, import it to a new project
                repository_id = project_id
                from ..dependencies.service_dependencies import get_github_service
                _github_service = get_github_service()

                repo_info = _github_service.get_repository_info(repository_id)
                
                if not repo_info:
                    raise ValueError(f"Repository with ID {repository_id} not found")
                
                if repo_info["status"] != "ready":
                    raise ValueError(f"Repository is not ready. Status: {repo_info['status']}")
                
                # Import repository files to the file service
                project_id = self.file_service.import_from_repository(
                    repository_id,
                    repo_info["owner"],
                    repo_info["repo"]
                )
                
                if not project_id:
                    raise ValueError("Failed to import repository files")
            
            # Get project information
            project_info = self.file_service.get_project(project_id)
            if not project_info:
                raise ValueError(f"Project with ID {project_id} not found")
            
            # Create analysis job record
            analysis_info = {
                "id": analysis_id,
                "project_id": project_id,
                "analysis_types": analysis_types,
                "status": "pending",
                "progress": 0,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "completed_at": None,
                "results": {},
                "error": None
            }
            
            # Add project metadata
            analysis_info["project_name"] = project_info.get("name", "")
            analysis_info["file_count"] = project_info.get("file_count", 0)
            analysis_info["languages"] = project_info.get("languages", [])
            
            # Save analysis job
            self.analysis_db.create_analysis_job(analysis_info)
            
            return analysis_id
            
        except ValueError as e:
            # Create a failed analysis job record
            analysis_info = {
                "id": analysis_id,
                "project_id": project_id,
                "analysis_types": analysis_types,
                "status": "failed",
                "progress": 0,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "completed_at": datetime.utcnow().isoformat(),
                "results": {},
                "error": str(e)
            }
            self.analysis_db.create_analysis_job(analysis_info)
            raise
