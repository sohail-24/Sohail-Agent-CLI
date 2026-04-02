"""Base agent class for all agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from rich.console import Console

from src.analyzers import RepoAnalyzer, RepoAnalysis
from src.workers import FileWorker, WorkerSafetyLevel

console = Console()


class AgentResult:
    """Result from agent execution."""
    
    def __init__(
        self,
        success: bool,
        message: str,
        error: str | None = None,
        files_created: list[Path] | None = None,
        files_skipped: list[Path] | None = None,
        data: dict[str, Any] | None = None,
    ):
        self.success = success
        self.message = message
        self.error = error
        self.files_created = files_created or []
        self.files_skipped = files_skipped or []
        self.data = data or {}
    
    @classmethod
    def success(
        cls,
        message: str,
        files_created: list[Path] | None = None,
        data: dict[str, Any] | None = None,
    ) -> AgentResult:
        return cls(
            success=True,
            message=message,
            files_created=files_created,
            data=data,
        )
    
    @classmethod
    def failure(cls, message: str, error: str | None = None) -> AgentResult:
        return cls(
            success=False,
            message=message,
            error=error,
        )


class BaseAgent(ABC):
    """Base class for all agents."""
    
    def __init__(
        self,
        name: str,
        description: str,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> None:
        self.name = name
        self.description = description
        self.dry_run = dry_run
        self.verbose = verbose
        self.file_worker = FileWorker(
            safety_level=WorkerSafetyLevel.WRITE_SAFE,
            dry_run=dry_run,
        )
        self.repo_analyzer = RepoAnalyzer()
    
    def log(self, message: str, style: str = "") -> None:
        """Log a message if verbose."""
        if self.verbose:
            if style:
                console.print(f"[{style}]{message}[/{style}]")
            else:
                console.print(message)
    
    def info(self, message: str) -> None:
        """Print info message."""
        console.print(f"[cyan]ℹ[/cyan] {message}")
    
    def success(self, message: str) -> None:
        """Print success message."""
        console.print(f"[green]✓[/green] {message}")
    
    def warning(self, message: str) -> None:
        """Print warning message."""
        console.print(f"[yellow]⚠[/yellow] {message}")
    
    def error(self, message: str) -> None:
        """Print error message."""
        console.print(f"[red]✗[/red] {message}")
    
    async def analyze_repo(self, path: Path) -> RepoAnalysis:
        """Analyze a repository."""
        self.log(f"Analyzing repository: {path}")
        return self.repo_analyzer.analyze(path)
    
    async def write_file(
        self,
        path: Path,
        content: str,
        overwrite: bool = False,
    ) -> tuple[bool, str]:
        """Write a file using the file worker."""
        if path.exists() and not overwrite:
            return False, f"File exists (use --overwrite): {path}"
        
        result = await self.file_worker.write(
            path=path,
            content=content,
            overwrite=overwrite,
        )
        
        if result.success:
            return True, f"Created: {path}"
        else:
            return False, result.message
    
    @abstractmethod
    async def execute(self, path: Path, **kwargs: Any) -> AgentResult:
        """Execute the agent's main task."""
        pass
