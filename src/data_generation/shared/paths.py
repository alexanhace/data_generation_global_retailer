from pathlib import Path

def _find_project_root() -> Path:
    """Walk up the directory tree until we find pyproject.toml."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / 'pyproject.toml').exists():
            return parent
    raise FileNotFoundError("Could not find project root - is pyproject.toml missing?")

PROJECT_ROOT = _find_project_root()