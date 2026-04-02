"""Kubernetes agent for generating K8s manifests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.agents.base_agent import AgentResult, BaseAgent
from src.generators import K8sGenerator


class K8sAgent(BaseAgent):
    """Agent that generates Kubernetes manifests."""
    
    def __init__(self, dry_run: bool = False, verbose: bool = False) -> None:
        super().__init__(
            name="k8s_agent",
            description="Generates Kubernetes deployment, service, and kustomization",
            dry_run=dry_run,
            verbose=verbose,
        )
        self.generator = K8sGenerator()
    
    async def execute(
        self,
        path: Path,
        app_name: str | None = None,
        port: int | None = None,
        overwrite: bool = False,
        **kwargs: Any,
    ) -> AgentResult:
        """Execute K8s generation."""
        self.info(f"Generating Kubernetes manifests for: {path}")
        
        # Analyze repository
        analysis = await self.analyze_repo(path)
        stack = analysis.stack.primary
        
        self.info(f"Detected stack: {stack.value}")
        
        # Generate K8s manifests
        deployment, service, kustomization = self.generator.generate(
            stack=stack,
            project_path=path,
            app_name=app_name,
            port=port,
        )
        
        # Create k8s directory
        k8s_dir = path / "k8s"
        if not self.dry_run:
            k8s_dir.mkdir(exist_ok=True)
        
        # Write files
        files_created = []
        files_skipped = []
        
        # deployment.yaml
        deployment_path = k8s_dir / "deployment.yaml"
        success, msg = await self.write_file(
            deployment_path,
            deployment,
            overwrite=overwrite,
        )
        if success:
            self.success(msg)
            files_created.append(deployment_path)
        else:
            self.warning(msg)
            files_skipped.append(deployment_path)
        
        # service.yaml
        service_path = k8s_dir / "service.yaml"
        success, msg = await self.write_file(
            service_path,
            service,
            overwrite=overwrite,
        )
        if success:
            self.success(msg)
            files_created.append(service_path)
        else:
            self.warning(msg)
            files_skipped.append(service_path)
        
        # kustomization.yaml
        kustomization_path = k8s_dir / "kustomization.yaml"
        success, msg = await self.write_file(
            kustomization_path,
            kustomization,
            overwrite=overwrite,
        )
        if success:
            self.success(msg)
            files_created.append(kustomization_path)
        else:
            self.warning(msg)
            files_skipped.append(kustomization_path)
        
        return AgentResult.success(
            message=f"Kubernetes manifests generated in k8s/",
            files_created=files_created,
            data={
                "stack": stack.value,
                "app_name": app_name or path.name.lower().replace(" ", "-"),
                "files_created": len(files_created),
                "files_skipped": len(files_skipped),
            },
        )
