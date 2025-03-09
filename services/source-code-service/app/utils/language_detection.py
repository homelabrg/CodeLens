# services/source-code-service/app/utils/language_detection.py
import os
import re
from typing import Optional, Dict, Set

# Extension to language mapping
EXTENSION_MAP: Dict[str, str] = {
    # Python
    '.py': 'Python',
    '.pyw': 'Python',
    '.pyx': 'Python',
    '.pxd': 'Python',
    
    # JavaScript
    '.js': 'JavaScript',
    '.jsx': 'JavaScript',
    '.mjs': 'JavaScript',
    
    # TypeScript
    '.ts': 'TypeScript',
    '.tsx': 'TypeScript',
    
    # Java
    '.java': 'Java',
    
    # C#
    '.cs': 'C#',
    
    # C++
    '.cpp': 'C++',
    '.cc': 'C++',
    '.cxx': 'C++',
    '.hpp': 'C++',
    '.hxx': 'C++',
    
    # C
    '.c': 'C',
    '.h': 'C',
    
    # Go
    '.go': 'Go',
    
    # Ruby
    '.rb': 'Ruby',
    '.rake': 'Ruby',
    
    # PHP
    '.php': 'PHP',
    
    # Swift
    '.swift': 'Swift',
    
    # Rust
    '.rs': 'Rust',
    
    # Kotlin
    '.kt': 'Kotlin',
    '.kts': 'Kotlin',
    
    # Scala
    '.scala': 'Scala',
    
    # HTML
    '.html': 'HTML',
    '.htm': 'HTML',
    
    # CSS
    '.css': 'CSS',
    
    # SCSS/SASS
    '.scss': 'SCSS',
    '.sass': 'SASS',
    
    # JSON
    '.json': 'JSON',
    
    # XML
    '.xml': 'XML',
    
    # YAML
    '.yaml': 'YAML',
    '.yml': 'YAML',
    
    # Markdown
    '.md': 'Markdown',
    '.markdown': 'Markdown',
    
    # Shell
    '.sh': 'Shell',
    '.bash': 'Shell',
    
    # PowerShell
    '.ps1': 'PowerShell',
    
    # SQL
    '.sql': 'SQL',
    
    # R
    '.r': 'R',
    '.R': 'R',
    
    # Perl
    '.pl': 'Perl',
    '.pm': 'Perl',
    
    # Haskell
    '.hs': 'Haskell',
    
    # Lua
    '.lua': 'Lua',
    
    # Groovy
    '.groovy': 'Groovy',
    
    # Dockerfile
    '.dockerfile': 'Dockerfile',
    
    # Terraform
    '.tf': 'Terraform',
    '.tfvars': 'Terraform',
    
    # Jupyter Notebook
    '.ipynb': 'Jupyter Notebook',
}

# Shebang to language mapping
SHEBANG_PATTERNS: Dict[str, str] = {
    r'^#!.*\bpython': 'Python',
    r'^#!.*\bnode': 'JavaScript',
    r'^#!.*\bruby': 'Ruby',
    r'^#!.*\bperl': 'Perl',
    r'^#!.*\bbash': 'Shell',
    r'^#!.*\bsh\b': 'Shell',
    r'^#!.*\bzsh\b': 'Shell',
    r'^#!.*\bphp': 'PHP',
    r'^#!.*\br\b': 'R',
}

# Content patterns to language mapping
CONTENT_PATTERNS: Dict[str, str] = {
    r'^\s*<\?php': 'PHP',
    r'^\s*package\s+[a-z0-9_\.]+;': 'Java',
    r'^\s*using\s+[a-zA-Z0-9_\.]+;': 'C#',
    r'^\s*import\s+React': 'JavaScript',
    r'^\s*import\s+{.*}\s+from\s+[\'"]react[\'"]': 'JavaScript',
    r'^\s*#include\s+<[a-zA-Z0-9_\.]+>': 'C++',
    r'^\s*from\s+__future__\s+import': 'Python',
    r'^\s*defmodule\s+[A-Z][a-zA-Z0-9_\.]*\s+do': 'Elixir',
    r'^\s*use\s+strict;': 'Perl',
    r'^\s*\(\s*ns\s+[a-z0-9_\.-]+': 'Clojure',
}

def detect_language(file_path: str) -> Optional[str]:
    """
    Detect the programming language of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Optional[str]: Detected language or None if unknown
    """
    # Check if file exists
    if not os.path.isfile(file_path):
        return None
    
    # First, try to determine by extension
    _, ext = os.path.splitext(file_path)
    if ext in EXTENSION_MAP:
        return EXTENSION_MAP[ext]
    
    # Special case for Dockerfile without extension
    if os.path.basename(file_path).lower() == 'dockerfile':
        return 'Dockerfile'
    
    # If extension doesn't match, try to read the file
    try:
        # Read the first few lines
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            first_lines = ''.join([f.readline() for _ in range(10)])
        
        # Check for shebang
        for pattern, language in SHEBANG_PATTERNS.items():
            if re.search(pattern, first_lines, re.MULTILINE):
                return language
        
        # Check for content patterns
        for pattern, language in CONTENT_PATTERNS.items():
            if re.search(pattern, first_lines, re.MULTILINE):
                return language
        
    except Exception:
        # If we can't read the file, return None
        return None
    
    # If we couldn't determine the language, return None
    return None

def get_all_languages() -> Set[str]:
    """
    Get a set of all supported languages.
    
    Returns:
        Set[str]: Set of all supported languages
    """
    languages = set(EXTENSION_MAP.values())
    languages.update(SHEBANG_PATTERNS.values())
    languages.update(CONTENT_PATTERNS.values())
    return languages