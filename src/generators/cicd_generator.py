"""CI/CD workflow generator."""

from __future__ import annotations

from pathlib import Path

from src.analyzers import StackType


class CicdGenerator:
    """Generator for CI/CD workflows."""
    
    def generate(
        self,
        stack: StackType,
        project_path: Path,
        has_docker: bool = False,
    ) -> tuple[str, str | None, str]:
        """
        Generate CI/CD workflows.
        
        Returns:
            Tuple of (ci_yml, docker_yml or None, release_yml)
        """
        ci = self._generate_ci(stack, has_docker)
        docker = self._generate_docker(stack) if has_docker else None
        release = self._generate_release(stack)
        
        return ci, docker, release
    
    def _generate_ci(self, stack: StackType, has_docker: bool) -> str:
        """Generate ci.yml."""
        if stack in (StackType.PYTHON, StackType.DJANGO, StackType.FASTAPI, StackType.FLASK):
            return self._generate_python_ci(has_docker)
        elif stack in (StackType.NODE, StackType.REACT, StackType.NEXTJS, StackType.VUE):
            return self._generate_node_ci(has_docker)
        elif stack == StackType.GO:
            return self._generate_go_ci(has_docker)
        elif stack == StackType.RUST:
            return self._generate_rust_ci(has_docker)
        else:
            return self._generate_generic_ci(has_docker)
    
    def _generate_python_ci(self, has_docker: bool) -> str:
        """Generate Python CI workflow."""
        docker_section = ""
        if has_docker:
            docker_section = """
      - name: Build Docker image
        run: docker build -t app:test .
        
      - name: Test Docker image
        run: docker run --rm app:test echo "Docker build successful"
"""
        
        return f"""name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Cache pip packages
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt', '**/pyproject.toml') }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt 2>/dev/null || pip install -e . 2>/dev/null || echo "No requirements"

      - name: Lint with ruff
        run: |
          pip install ruff
          ruff check . || true
          ruff format --check . || true

      - name: Type check with mypy
        run: |
          pip install mypy
          mypy . || true

      - name: Test with pytest
        run: |
          pip install pytest pytest-cov
          pytest --cov=. --cov-report=xml || true
{docker_section}
"""
    
    def _generate_node_ci(self, has_docker: bool) -> str:
        """Generate Node.js CI workflow."""
        docker_section = ""
        if has_docker:
            docker_section = """
      - name: Build Docker image
        run: docker build -t app:test .
        
      - name: Test Docker image
        run: docker run --rm app:test echo "Docker build successful"
"""
        
        return f"""name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: ['18', '20']

    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Lint
        run: npm run lint || true

      - name: Type check
        run: npm run type-check || true

      - name: Test
        run: npm test || true

      - name: Build
        run: npm run build || true
{docker_section}
"""
    
    def _generate_go_ci(self, has_docker: bool) -> str:
        """Generate Go CI workflow."""
        docker_section = ""
        if has_docker:
            docker_section = """
      - name: Build Docker image
        run: docker build -t app:test .
"""
        
        return f"""name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Go
        uses: actions/setup-go@v5
        with:
          go-version: '1.21'

      - name: Cache Go modules
        uses: actions/cache@v4
        with:
          path: ~/go/pkg/mod
          key: ${{ runner.os }}-go-${{ hashFiles('**/go.sum') }}

      - name: Download dependencies
        run: go mod download

      - name: Build
        run: go build -v ./...

      - name: Test
        run: go test -v -race -coverprofile=coverage.out ./...
{docker_section}
"""
    
    def _generate_rust_ci(self, has_docker: bool) -> str:
        """Generate Rust CI workflow."""
        docker_section = ""
        if has_docker:
            docker_section = """
      - name: Build Docker image
        run: docker build -t app:test .
"""
        
        return f"""name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Cache cargo
        uses: actions/cache@v4
        with:
          path: |
            ~/.cargo/registry
            ~/.cargo/git
            target
          key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}

      - name: Build
        run: cargo build --verbose

      - name: Test
        run: cargo test --verbose

      - name: Check formatting
        run: cargo fmt -- --check

      - name: Run clippy
        run: cargo clippy -- -D warnings || true
{docker_section}
"""
    
    def _generate_generic_ci(self, has_docker: bool) -> str:
        """Generate generic CI workflow."""
        docker_section = ""
        if has_docker:
            docker_section = """
      - name: Build Docker image
        run: docker build -t app:test .
"""
        
        return f"""name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run tests
        run: echo "Add your test commands here"

      - name: Build
        run: echo "Add your build commands here"
{docker_section}
"""
    
    def _generate_docker(self, stack: StackType) -> str:
        """Generate docker.yml for build and push."""
        return """name: Docker

on:
  push:
    branches: [main]
    tags: ['v*']

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
"""
    
    def _generate_release(self, stack: StackType) -> str:
        """Generate release.yml."""
        return """name: Release

on:
  push:
    tags: ['v*']

permissions:
  contents: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Create Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          draft: false
          prerelease: false
"""
