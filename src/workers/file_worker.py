"""File worker for safe file operations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .base_worker import BaseWorker, WorkerResult, WorkerSafetyLevel


class FileWorker(BaseWorker):
    """
    Worker for safe file operations.
    
    Provides methods for reading, writing, and managing files
    with safety checks and dry-run support.
    """
    
    def __init__(
        self,
        safety_level: WorkerSafetyLevel = WorkerSafetyLevel.WRITE_SAFE,
        dry_run: bool = False,
        base_path: Path | None = None,
    ) -> None:
        """
        Initialize the file worker.
        
        Args:
            safety_level: The safety level for operations
            dry_run: If True, don't actually modify files
            base_path: Optional base path to restrict operations to
        """
        super().__init__(safety_level, dry_run)
        self.base_path = base_path
    
    async def execute(self, operation: str, **kwargs: Any) -> WorkerResult:
        """
        Execute a file operation.
        
        Args:
            operation: The operation to execute
            **kwargs: Operation-specific arguments
        
        Returns:
            The result of the operation
        """
        operations = {
            "read": self.read,
            "write": self.write,
            "exists": self.exists,
            "mkdir": self.mkdir,
            "list": self.list_dir,
            "delete": self.delete,
        }
        
        if operation not in operations:
            return WorkerResult.failure_result(
                f"Unknown operation: {operation}"
            )
        
        return await operations[operation](**kwargs)
    
    async def read(self, path: Path | str) -> WorkerResult:
        """
        Read a file.
        
        Args:
            path: Path to the file
        
        Returns:
            WorkerResult with file content
        """
        path = self._resolve_path(path)
        
        try:
            content = path.read_text(encoding="utf-8")
            return WorkerResult.success_result(
                f"Read {path}",
                {"content": content, "path": str(path)},
            )
        except FileNotFoundError:
            return WorkerResult.failure_result(
                f"File not found: {path}",
                "FileNotFoundError",
            )
        except Exception as e:
            return WorkerResult.failure_result(
                f"Error reading {path}: {e}",
                str(e),
            )
    
    async def write(
        self,
        path: Path | str,
        content: str,
        overwrite: bool = False,
    ) -> WorkerResult:
        """
        Write content to a file.
        
        Args:
            path: Path to the file
            content: Content to write
            overwrite: Whether to overwrite existing files
        
        Returns:
            WorkerResult with operation status
        """
        path = self._resolve_path(path)
        
        # Check safety level
        # WRITE_SAFE: can write new files
        # WRITE_UNSAFE: can overwrite existing files
        if path.exists() and overwrite:
            self._check_safety(WorkerSafetyLevel.WRITE_UNSAFE)
        # else: WRITE_SAFE is sufficient for new files or read-only
        
        if self.dry_run:
            return WorkerResult.success_result(
                f"[DRY RUN] Would write to {path}",
                {"path": str(path), "size": len(content)},
            )
        
        try:
            # Ensure parent directory exists
            path.parent.mkdir(parents=True, exist_ok=True)
            
            path.write_text(content, encoding="utf-8")
            
            return WorkerResult.success_result(
                f"Wrote {path}",
                {"path": str(path), "size": len(content)},
            )
        except Exception as e:
            return WorkerResult.failure_result(
                f"Error writing {path}: {e}",
                str(e),
            )
    
    async def exists(self, path: Path | str) -> WorkerResult:
        """
        Check if a path exists.
        
        Args:
            path: Path to check
        
        Returns:
            WorkerResult with existence status
        """
        path = self._resolve_path(path)
        
        return WorkerResult.success_result(
            f"Checked {path}",
            {"exists": path.exists(), "path": str(path)},
        )
    
    async def mkdir(
        self,
        path: Path | str,
        parents: bool = True,
        exist_ok: bool = True,
    ) -> WorkerResult:
        """
        Create a directory.
        
        Args:
            path: Path to create
            parents: Create parent directories
            exist_ok: Don't error if directory exists
        
        Returns:
            WorkerResult with operation status
        """
        path = self._resolve_path(path)
        
        self._check_safety(WorkerSafetyLevel.WRITE_SAFE)
        
        if self.dry_run:
            return WorkerResult.success_result(
                f"[DRY RUN] Would create directory {path}",
                {"path": str(path)},
            )
        
        try:
            path.mkdir(parents=parents, exist_ok=exist_ok)
            
            return WorkerResult.success_result(
                f"Created directory {path}",
                {"path": str(path)},
            )
        except Exception as e:
            return WorkerResult.failure_result(
                f"Error creating directory {path}: {e}",
                str(e),
            )
    
    async def list_dir(
        self,
        path: Path | str,
        pattern: str = "*",
    ) -> WorkerResult:
        """
        List directory contents.
        
        Args:
            path: Directory to list
            pattern: Glob pattern to match
        
        Returns:
            WorkerResult with directory listing
        """
        path = self._resolve_path(path)
        
        try:
            entries = list(path.glob(pattern))
            
            files = [str(e.relative_to(path)) for e in entries if e.is_file()]
            dirs = [str(e.relative_to(path)) for e in entries if e.is_dir()]
            
            return WorkerResult.success_result(
                f"Listed {path}",
                {
                    "path": str(path),
                    "files": files,
                    "directories": dirs,
                },
            )
        except Exception as e:
            return WorkerResult.failure_result(
                f"Error listing {path}: {e}",
                str(e),
            )
    
    async def delete(
        self,
        path: Path | str,
        recursive: bool = False,
    ) -> WorkerResult:
        """
        Delete a file or directory.
        
        Args:
            path: Path to delete
            recursive: Recursively delete directories
        
        Returns:
            WorkerResult with operation status
        """
        path = self._resolve_path(path)
        
        self._check_safety(WorkerSafetyLevel.WRITE_UNSAFE)
        
        if self.dry_run:
            return WorkerResult.success_result(
                f"[DRY RUN] Would delete {path}",
                {"path": str(path)},
            )
        
        try:
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                if recursive:
                    import shutil
                    shutil.rmtree(path)
                else:
                    path.rmdir()
            
            return WorkerResult.success_result(
                f"Deleted {path}",
                {"path": str(path)},
            )
        except Exception as e:
            return WorkerResult.failure_result(
                f"Error deleting {path}: {e}",
                str(e),
            )
    
    def _resolve_path(self, path: Path | str) -> Path:
        """
        Resolve a path, optionally relative to base_path.
        
        Args:
            path: The path to resolve
        
        Returns:
            Resolved Path object
        """
        path = Path(path)
        
        if self.base_path and not path.is_absolute():
            path = self.base_path / path
        
        return path.resolve()
