"""Technology stack detection for repositories."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any


class StackType(Enum):
    """Supported technology stacks."""
    PYTHON = "python"
    DJANGO = "django"
    FASTAPI = "fastapi"
    FLASK = "flask"
    NODE = "node"
    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"
    NEXTJS = "nextjs"
    GO = "go"
    RUST = "rust"
    JAVA = "java"
    KOTLIN = "kotlin"
    SCALA = "scala"
    RUBY = "ruby"
    RAILS = "rails"
    PHP = "php"
    LARAVEL = "laravel"
    ELIXIR = "elixir"
    TYPESCRIPT = "typescript"
    UNKNOWN = "unknown"


@dataclass
class DetectedStack:
    """Result of technology stack detection."""
    primary: StackType
    secondary: list[StackType] = field(default_factory=list)
    confidence: float = 0.0
    indicators: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "primary": self.primary.value,
            "secondary": [s.value for s in self.secondary],
            "confidence": self.confidence,
            "indicators": self.indicators,
        }


class StackDetector:
    """
    Detects the technology stack of a project.
    
    Uses file presence and content analysis to determine
    the primary and secondary technology stacks.
    """
    
    # Stack detection rules
    STACK_RULES: dict[StackType, dict[str, Any]] = {
        StackType.DJANGO: {
            "files": ["manage.py", "wsgi.py", "asgi.py"],
            "patterns_in_files": {
                "requirements.txt": ["django"],
                "pyproject.toml": ["django"],
            },
            "indicators": ["Django project detected"],
        },
        StackType.FASTAPI: {
            "files": [],
            "patterns_in_files": {
                "requirements.txt": ["fastapi", "uvicorn"],
                "pyproject.toml": ["fastapi", "uvicorn"],
            },
            "indicators": ["FastAPI application detected"],
        },
        StackType.FLASK: {
            "files": [],
            "patterns_in_files": {
                "requirements.txt": ["flask"],
                "pyproject.toml": ["flask"],
            },
            "indicators": ["Flask application detected"],
        },
        StackType.REACT: {
            "files": [],
            "patterns_in_files": {
                "package.json": ["react", "react-dom"],
            },
            "indicators": ["React frontend detected"],
        },
        StackType.VUE: {
            "files": [],
            "patterns_in_files": {
                "package.json": ["vue"],
            },
            "indicators": ["Vue.js frontend detected"],
        },
        StackType.ANGULAR: {
            "files": ["angular.json"],
            "patterns_in_files": {},
            "indicators": ["Angular application detected"],
        },
        StackType.NEXTJS: {
            "files": ["next.config.js", "next.config.ts", "next.config.mjs"],
            "patterns_in_files": {
                "package.json": ["next"],
            },
            "indicators": ["Next.js application detected"],
        },
        StackType.NODE: {
            "files": ["package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"],
            "patterns_in_files": {},
            "indicators": ["Node.js project detected"],
        },
        StackType.GO: {
            "files": ["go.mod", "go.sum"],
            "patterns_in_files": {},
            "indicators": ["Go project detected"],
        },
        StackType.RUST: {
            "files": ["Cargo.toml", "Cargo.lock"],
            "patterns_in_files": {},
            "indicators": ["Rust project detected"],
        },
        StackType.JAVA: {
            "files": ["pom.xml", "build.gradle", "gradlew"],
            "patterns_in_files": {},
            "indicators": ["Java project detected"],
        },
        StackType.RUBY: {
            "files": ["Gemfile"],
            "patterns_in_files": {},
            "indicators": ["Ruby project detected"],
        },
        StackType.RAILS: {
            "files": ["config/routes.rb", "config/application.rb"],
            "patterns_in_files": {
                "Gemfile": ["rails"],
            },
            "indicators": ["Ruby on Rails application detected"],
        },
        StackType.PHP: {
            "files": ["composer.json"],
            "patterns_in_files": {},
            "indicators": ["PHP project detected"],
        },
        StackType.LARAVEL: {
            "files": ["artisan"],
            "patterns_in_files": {
                "composer.json": ["laravel"],
            },
            "indicators": ["Laravel application detected"],
        },
        StackType.PYTHON: {
            "files": ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"],
            "patterns_in_files": {},
            "indicators": ["Python project detected"],
        },
    }
    
    def detect(self, directory: Path) -> DetectedStack:
        """
        Detect the technology stack of a project.
        
        Args:
            directory: The project directory to analyze
        
        Returns:
            DetectedStack with primary and secondary stacks
        """
        indicators: list[str] = []
        detected: dict[StackType, float] = {}
        
        # Check for each stack type
        for stack_type, rules in self.STACK_RULES.items():
            score = 0.0
            stack_indicators: list[str] = []
            
            # Check for characteristic files
            for filename in rules["files"]:
                if (directory / filename).exists():
                    score += 1.0
                    stack_indicators.append(f"Found {filename}")
            
            # Check for patterns in files
            for filename, patterns in rules["patterns_in_files"].items():
                file_path = directory / filename
                if file_path.exists():
                    try:
                        content = file_path.read_text().lower()
                        for pattern in patterns:
                            if pattern.lower() in content:
                                score += 1.5
                                stack_indicators.append(f"Found {pattern} in {filename}")
                    except Exception:
                        pass
            
            if score > 0:
                detected[stack_type] = score
                indicators.extend(stack_indicators)
        
        # Determine primary and secondary stacks
        if not detected:
            return DetectedStack(
                primary=StackType.UNKNOWN,
                secondary=[],
                confidence=0.0,
                indicators=["No recognizable stack detected"],
            )
        
        # Sort by score
        sorted_stacks = sorted(detected.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_stacks[0][0]
        primary_score = sorted_stacks[0][1]
        
        # Calculate confidence
        confidence = min(primary_score / 3.0, 1.0)
        
        # Secondary stacks (other detected stacks with significant scores)
        secondary = [
            stack for stack, score in sorted_stacks[1:]
            if score >= primary_score * 0.5
        ]
        
        return DetectedStack(
            primary=primary,
            secondary=secondary,
            confidence=confidence,
            indicators=indicators,
        )
    
    def get_dependencies(self, directory: Path, stack: StackType) -> list[str]:
        """
        Extract dependencies from project files.
        
        Args:
            directory: The project directory
            stack: The detected stack type
        
        Returns:
            List of dependency names
        """
        deps: list[str] = []
        
        if stack in (StackType.PYTHON, StackType.DJANGO, StackType.FASTAPI, StackType.FLASK):
            deps = self._get_python_deps(directory)
        elif stack in (StackType.NODE, StackType.REACT, StackType.VUE, StackType.NEXTJS):
            deps = self._get_node_deps(directory)
        elif stack == StackType.GO:
            deps = self._get_go_deps(directory)
        elif stack == StackType.RUST:
            deps = self._get_rust_deps(directory)
        elif stack in (StackType.RUBY, StackType.RAILS):
            deps = self._get_ruby_deps(directory)
        elif stack in (StackType.PHP, StackType.LARAVEL):
            deps = self._get_php_deps(directory)
        
        return deps[:20]  # Limit to top 20
    
    def _get_python_deps(self, directory: Path) -> list[str]:
        """Get Python dependencies."""
        deps: list[str] = []
        
        # Try requirements.txt
        req_file = directory / "requirements.txt"
        if req_file.exists():
            try:
                content = req_file.read_text()
                for line in content.split("\n"):
                    line = line.strip()
                    if line and not line.startswith("#"):
                        pkg = line.split("=")[0].split("<")[0].split(">")[0].split("[")[0].strip()
                        if pkg:
                            deps.append(pkg)
            except Exception:
                pass
        
        # Try pyproject.toml
        pyproject = directory / "pyproject.toml"
        if pyproject.exists():
            try:
                content = pyproject.read_text()
                in_deps = False
                for line in content.split("\n"):
                    if "dependencies" in line and "[" in line:
                        in_deps = True
                    elif in_deps:
                        if line.strip().startswith("[") and "dependencies" not in line:
                            in_deps = False
                        elif "=" in line or line.strip().startswith('"'):
                            pkg = line.split("=")[0].strip().strip('"\'')
                            if pkg and pkg not in ("python",):
                                deps.append(pkg)
            except Exception:
                pass
        
        return deps
    
    def _get_node_deps(self, directory: Path) -> list[str]:
        """Get Node.js dependencies."""
        deps: list[str] = []
        
        package_json = directory / "package.json"
        if package_json.exists():
            try:
                data = json.loads(package_json.read_text())
                if "dependencies" in data:
                    deps.extend(data["dependencies"].keys())
                if "devDependencies" in data:
                    deps.extend(data["devDependencies"].keys())
            except Exception:
                pass
        
        return deps
    
    def _get_go_deps(self, directory: Path) -> list[str]:
        """Get Go dependencies."""
        deps: list[str] = []
        
        go_mod = directory / "go.mod"
        if go_mod.exists():
            try:
                content = go_mod.read_text()
                for line in content.split("\n"):
                    if line.strip() and not line.startswith("module") and not line.startswith("go "):
                        parts = line.strip().split()
                        if parts:
                            deps.append(parts[0])
            except Exception:
                pass
        
        return deps
    
    def _get_rust_deps(self, directory: Path) -> list[str]:
        """Get Rust dependencies."""
        deps: list[str] = []
        
        cargo_toml = directory / "Cargo.toml"
        if cargo_toml.exists():
            try:
                content = cargo_toml.read_text()
                in_deps = False
                for line in content.split("\n"):
                    if "[dependencies]" in line:
                        in_deps = True
                    elif in_deps and line.strip().startswith("["):
                        in_deps = False
                    elif in_deps and "=" in line:
                        pkg = line.split("=")[0].strip()
                        if pkg:
                            deps.append(pkg)
            except Exception:
                pass
        
        return deps
    
    def _get_ruby_deps(self, directory: Path) -> list[str]:
        """Get Ruby dependencies."""
        deps: list[str] = []
        
        gemfile = directory / "Gemfile"
        if gemfile.exists():
            try:
                content = gemfile.read_text()
                for line in content.split("\n"):
                    if line.strip().startswith("gem "):
                        parts = line.split('"')
                        if len(parts) >= 2:
                            deps.append(parts[1])
            except Exception:
                pass
        
        return deps
    
    def _get_php_deps(self, directory: Path) -> list[str]:
        """Get PHP dependencies."""
        deps: list[str] = []
        
        composer = directory / "composer.json"
        if composer.exists():
            try:
                data = json.loads(composer.read_text())
                if "require" in data:
                    deps.extend(data["require"].keys())
            except Exception:
                pass
        
        return deps
