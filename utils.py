"""
Utility functions for repository analysis.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
import subprocess


def get_repo_name(repo_path: str) -> str:
    """Extract repository name from path."""
    return Path(repo_path).name


def save_json_output(data: dict, output_path: str) -> None:
    """Save analysis output as JSON (for further processing)."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)
    print(f"✅ Output saved to: {output_path}")


def format_guidance_for_display(guidance: str) -> str:
    """Format guidance text for terminal display."""
    return guidance


def validate_repo_path(path: str) -> bool:
    """Validate that a path is a valid repository."""
    repo_path = Path(path)
    return repo_path.exists() and repo_path.is_dir()


def is_git_repo(path: str) -> bool:
    """Check if path is a git repository."""
    git_dir = Path(path) / ".git"
    return git_dir.exists()


def get_repo_size(path: str) -> int:
    """Get total size of repository in bytes."""
    total_size = 0
    for file_path in Path(path).rglob('*'):
        if file_path.is_file():
            try:
                total_size += file_path.stat().st_size
            except (OSError, FileNotFoundError):
                pass
    return total_size


def count_files_by_extension(path: str) -> Dict[str, int]:
    """Count files by extension."""
    extensions = {}
    for file_path in Path(path).rglob('*'):
        if file_path.is_file():
            ext = file_path.suffix or 'no_extension'
            extensions[ext] = extensions.get(ext, 0) + 1
    return dict(sorted(extensions.items(), key=lambda x: x[1], reverse=True))


def get_code_stats(path: str) -> Dict[str, Any]:
    """Get statistics about code in repository."""
    stats = {
        "total_files": 0,
        "total_lines": 0,
        "by_extension": {}
    }
    
    for file_path in Path(path).rglob('*'):
        if file_path.is_file() and not any(part.startswith('.') for part in file_path.parts):
            stats["total_files"] += 1
            ext = file_path.suffix or 'no_extension'
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
                    stats["total_lines"] += lines
                    
                    if ext not in stats["by_extension"]:
                        stats["by_extension"][ext] = {"files": 0, "lines": 0}
                    stats["by_extension"][ext]["files"] += 1
                    stats["by_extension"][ext]["lines"] += lines
            except (OSError, IOError):
                pass
    
    return stats


def create_summary_metadata(state: dict) -> Dict[str, Any]:
    """Create metadata summary from agent state."""
    return {
        "analysis_timestamp": str(state.get("timestamp", "N/A")),
        "repository": state.get("target_repo_path", "N/A"),
        "language": state.get("repo_type", {}).get("language", "Unknown"),
        "frameworks": state.get("repo_type", {}).get("frameworks", []),
        "has_tests": state.get("repo_type", {}).get("has_tests", False),
        "has_docs": state.get("repo_type", {}).get("has_docs", False),
        "files_analyzed": len(state.get("file_contents", {})),
        "entry_points": state.get("key_insights", {}).get("entry_points", []),
        "main_modules": state.get("key_insights", {}).get("main_modules", []),
    }
