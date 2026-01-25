# Codebase Linter & Metadata Extractor PRD

## 1. Overview
The goal is to develop a custom Linter System that analyzes the project's source code. It serves two primary purposes:
1.  **Code Quality Analysis**: Identify areas for improvement and potential issues.
2.  **Metadata Extraction**: Extract structural information (classes, functions, methods, parameters, docstrings) to create a comprehensive index of the codebase. This index will facilitate the future exposure of these components as MCP (Model Context Protocol) tools.

## 2. Goals
- **Standardization**: Ensure code follows project standards (docstrings, typing).
- **Discoverability**: Create a queryable index of all code components.
- **Automation**: Automate the process of understanding the codebase structure for AI agents.

## 3. Functional Requirements

### 3.1. Static Analysis (AST Based)
- The system must parse Python files using the `ast` module.
- It must not execute the code, only analyze it statically.

### 3.2. Metadata Extraction
For each Python file, extract:
- **Global Variables**: Name, type (if annotated).
- **Imports**: List of modules imported.
- **Functions**:
    - Name
    - Arguments (name, type annotation, default values)
    - Return type annotation
    - Docstring
    - Line number (start/end)
- **Classes**:
    - Name
    - Docstring
    - Methods (same attributes as functions)
    - Class attributes

### 3.3. Quality Checks
- **Missing Docstrings**: Report functions/classes without docstrings.
- **Missing Type Hints**: Report arguments/returns without type annotations.
- **Complexity**: (Optional) Simple cyclomatic complexity warning if too high.

### 3.6. Dependency Management
- **Extraction**: Identify all imported packages.
- **Classification**: Distinguish between standard library, project-local modules, and third-party packages.
- **Automation**: Provide a script (`update_requirements.py`) to:
    1. Scan the codebase for third-party imports.
    2. Compare with existing `requirements.txt`.
    3. Add missing packages (potentially querying PyPI for versions or defaulting to latest).

### 3.5. Output
- **Format**: JSON.
- **Structure**:
  ```json
  {
    "file_path": "src/utils/example.py",
    "imports": ["os", "json", "pandas"],
    "classes": [ ... ],
    "functions": [ ... ],
    "issues": [
        { "type": "missing_docstring", "target": "my_function", "line": 10 }
    ]
  }
  ```

### 3.7. Reporting
- Generate a human-readable summary (Markdown) alongside the raw JSON data.

## 4. Technical Architecture
- **Language**: Python 3.12+
- **Location**: `src/utils/linter.py` (or a dedicated `src/linter/` package if complex).
- **Dependencies**: Standard library `ast`, `json`, `pathlib`. Pydantic (optional, for schema validation if available in project).

## 5. Success Metrics
- Successfully extracts metadata from 100% of valid Python files in `src/`.
- Generated JSON is valid and parsable.
- Identifies missing docstrings/types correctly in test cases.
