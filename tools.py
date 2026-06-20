"""
Custom tools for repo analysis integrated with MCP servers.
These tools wrap MCP server capabilities and provide agent-friendly interfaces.
"""

import os
import subprocess
import json
from typing import Optional
from pathlib import Path


class FilesystemToolkit:
    """Interact with repository files via MCP filesystem server."""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
    
    def list_directory(self, path: str = ".") -> dict:
        """List files and folders in a directory."""
        target_path = self.repo_path / path if path != "." else self.repo_path
        
        try:
            items = {
                "directories": [],
                "files": [],
                "path": str(target_path.relative_to(self.repo_path))
            }
            
            for item in sorted(target_path.iterdir()):
                relative = item.relative_to(self.repo_path)
                if item.is_dir() and not item.name.startswith('.'):
                    items["directories"].append(str(relative))
                elif item.is_file():
                    items["files"].append({
                        "name": str(relative),
                        "size": item.stat().st_size
                    })
            
            return items
        except Exception as e:
            return {"error": str(e)}
    
    def read_file(self, file_path: str) -> dict:
        """Read contents of a file."""
        target_file = self.repo_path / file_path
        
        try:
            if not target_file.exists():
                return {"error": f"File not found: {file_path}"}
            
            # For large files, limit to first 5000 lines
            with open(target_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()[:5000]
                content = ''.join(lines)
            
            return {
                "path": file_path,
                "size": len(content),
                "lines": len(lines),
                "content": content,
                "truncated": len(lines) == 5000
            }
        except Exception as e:
            return {"error": str(e)}
    
    def find_files(self, pattern: str, max_results: int = 20) -> dict:
        """Find files matching a pattern."""
        try:
            results = []
            for root, dirs, files in os.walk(self.repo_path):
                # Skip hidden and common non-essential dirs
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in 
                          ['node_modules', '__pycache__', 'dist', 'build', 'venv', '.venv']]
                
                for file in files:
                    if pattern.lower() in file.lower():
                        path = Path(root) / file
                        relative = path.relative_to(self.repo_path)
                        results.append(str(relative))
                        if len(results) >= max_results:
                            return {"results": results, "truncated": True}
            
            return {"results": results, "truncated": False}
        except Exception as e:
            return {"error": str(e)}


class GitToolkit:
    """Interact with git history and metadata."""
    
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
    
    def get_git_log(self, max_commits: int = 20) -> dict:
        """Get recent git commits."""
        try:
            result = subprocess.run(
                ["git", "log", f"--max-count={max_commits}", "--oneline", "--decorate"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return {"error": "Not a git repository or git not available"}
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    commits.append(line)
            
            return {
                "commits": commits,
                "count": len(commits)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_git_branches(self) -> dict:
        """Get list of branches."""
        try:
            result = subprocess.run(
                ["git", "branch", "-a"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            branches = [b.strip() for b in result.stdout.split('\n') if b.strip()]
            return {"branches": branches}
        except Exception as e:
            return {"error": str(e)}
    
    def get_git_status(self) -> dict:
        """Get repository status."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            changes = [line for line in result.stdout.split('\n') if line.strip()]
            return {
                "status": "clean" if not changes else "dirty",
                "changes_count": len(changes),
                "changes": changes[:10]  # First 10
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_recent_changes(self, days: int = 30) -> dict:
        """Get summary of recent changes."""
        try:
            result = subprocess.run(
                ["git", "log", f"--since={days}.days.ago", "--pretty=format:%h|%ai|%s"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            changes = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        changes.append({
                            "commit": parts[0],
                            "date": parts[1],
                            "message": parts[2]
                        })
            
            return {"recent_changes": changes, "count": len(changes)}
        except Exception as e:
            return {"error": str(e)}


class RepoAnalyzerTools:
    """High-level analysis tools."""
    
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.fs = FilesystemToolkit(repo_path)
        self.git = GitToolkit(repo_path)
    
    def detect_repo_type(self) -> dict:
        """Detect repository type and key characteristics."""
        repo_type = {
            "language": "unknown",
            "frameworks": [],
            "build_system": None,
            "has_tests": False,
            "has_docs": False,
            "detected_files": {}
        }
        
        files = self.fs.find_files("", max_results=100)
        if "results" in files:
            file_list = files["results"]
            
            # Detect language/framework
            if any("package.json" in f for f in file_list):
                repo_type["language"] = "JavaScript/TypeScript"
                repo_type["frameworks"].append("Node.js")
            if any("pyproject.toml" in f or "requirements.txt" in f for f in file_list):
                repo_type["language"] = "Python"
            if any("pom.xml" in f for f in file_list):
                repo_type["language"] = "Java"
                repo_type["build_system"] = "Maven"
            if any("go.mod" in f for f in file_list):
                repo_type["language"] = "Go"
            if any("Cargo.toml" in f for f in file_list):
                repo_type["language"] = "Rust"
            
            # Detect build systems
            if any("Dockerfile" in f for f in file_list):
                repo_type["frameworks"].append("Docker")
            if any("docker-compose" in f for f in file_list):
                repo_type["frameworks"].append("Docker Compose")
            
            # Detect tests and docs
            repo_type["has_tests"] = any("test" in f.lower() for f in file_list)
            repo_type["has_docs"] = any("doc" in f.lower() or "README" in f for f in file_list)
        
        return repo_type
    
    def get_core_files_to_read(self) -> dict:
        """Identify core files that should be read first."""
        priority_files = [
            "README.md",
            "README.rst",
            "CONTRIBUTING.md",
            "ARCHITECTURE.md",
            "pyproject.toml",
            "setup.py",
            "requirements.txt",
            "package.json",
            "package-lock.json",
            "pom.xml",
            "Dockerfile",
            "Makefile",
            "main.py",
            "index.js",
            "app.py",
        ]
        
        files = self.fs.find_files("", max_results=200)
        available_files = files.get("results", [])
        
        core_files = []
        for priority in priority_files:
            for file in available_files:
                if priority.lower() == file.split('/')[-1].lower():
                    core_files.append(file)
                    break
        
        return {
            "core_files": core_files,
            "count": len(core_files)
        }
