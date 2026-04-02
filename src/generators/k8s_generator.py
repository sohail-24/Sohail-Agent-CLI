"""Kubernetes manifest generator."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from src.analyzers import StackType


@dataclass
class K8sConfig:
    """Configuration for K8s generation."""
    app_name: str
    image: str
    port: int = 8000
    replicas: int = 1
    namespace: str = "default"
    service_type: str = "ClusterIP"
    ingress_enabled: bool = False
    ingress_host: str = ""


class K8sGenerator:
    """Generator for Kubernetes manifests."""
    
    def generate(
        self,
        stack: StackType,
        project_path: Path,
        app_name: str | None = None,
        port: int | None = None,
    ) -> tuple[str, str, str]:
        """
        Generate K8s manifests.
        
        Returns:
            Tuple of (deployment, service, kustomization)
        """
        # Get app name from path if not provided
        if app_name is None:
            app_name = self._slugify(project_path.name)
        
        # Get port based on stack
        default_port = self._get_default_port(stack)
        port = port or default_port
        
        config = K8sConfig(
            app_name=app_name,
            image=f"{app_name}:latest",
            port=port,
        )
        
        deployment = self._generate_deployment(config)
        service = self._generate_service(config)
        kustomization = self._generate_kustomization(config)
        
        return deployment, service, kustomization
    
    def _get_default_port(self, stack: StackType) -> int:
        """Get default port for stack."""
        ports = {
            StackType.DJANGO: 8000,
            StackType.FASTAPI: 8000,
            StackType.FLASK: 5000,
            StackType.NODE: 3000,
            StackType.REACT: 80,
            StackType.NEXTJS: 3000,
            StackType.VUE: 80,
            StackType.GO: 8080,
            StackType.RUST: 8080,
            StackType.PYTHON: 8000,
        }
        return ports.get(stack, 8080)
    
    def _slugify(self, text: str) -> str:
        """Convert text to k8s-friendly name."""
        return text.lower().replace(" ", "-").replace("_", "-")
    
    def _generate_deployment(self, config: K8sConfig) -> str:
        """Generate deployment.yaml."""
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": config.app_name,
                "namespace": config.namespace,
                "labels": {
                    "app": config.app_name,
                },
            },
            "spec": {
                "replicas": config.replicas,
                "selector": {
                    "matchLabels": {
                        "app": config.app_name,
                    },
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": config.app_name,
                        },
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": config.app_name,
                                "image": config.image,
                                "ports": [
                                    {
                                        "containerPort": config.port,
                                    },
                                ],
                                "env": [
                                    {"name": "PORT", "value": str(config.port)},
                                ],
                                "resources": {
                                    "requests": {
                                        "memory": "128Mi",
                                        "cpu": "100m",
                                    },
                                    "limits": {
                                        "memory": "512Mi",
                                        "cpu": "500m",
                                    },
                                },
                                # Readiness probe placeholder
                                "readinessProbe": {
                                    "httpGet": {
                                        "path": "/health",
                                        "port": config.port,
                                    },
                                    "initialDelaySeconds": 5,
                                    "periodSeconds": 10,
                                },
                                # Liveness probe placeholder
                                "livenessProbe": {
                                    "httpGet": {
                                        "path": "/health",
                                        "port": config.port,
                                    },
                                    "initialDelaySeconds": 15,
                                    "periodSeconds": 20,
                                },
                            },
                        ],
                    },
                },
            },
        }
        
        return yaml.dump(deployment, default_flow_style=False, sort_keys=False)
    
    def _generate_service(self, config: K8sConfig) -> str:
        """Generate service.yaml."""
        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": config.app_name,
                "namespace": config.namespace,
                "labels": {
                    "app": config.app_name,
                },
            },
            "spec": {
                "type": config.service_type,
                "ports": [
                    {
                        "port": config.port,
                        "targetPort": config.port,
                        "protocol": "TCP",
                        "name": "http",
                    },
                ],
                "selector": {
                    "app": config.app_name,
                },
            },
        }
        
        return yaml.dump(service, default_flow_style=False, sort_keys=False)
    
    def _generate_kustomization(self, config: K8sConfig) -> str:
        """Generate kustomization.yaml."""
        kustomization = {
            "apiVersion": "kustomize.config.k8s.io/v1beta1",
            "kind": "Kustomization",
            "resources": [
                "deployment.yaml",
                "service.yaml",
            ],
            "commonLabels": {
                "app": config.app_name,
            },
            "images": [
                {
                    "name": config.image,
                    "newTag": "latest",
                },
            ],
        }
        
        return yaml.dump(kustomization, default_flow_style=False, sort_keys=False)
    
    def generate_ingress(self, config: K8sConfig) -> str:
        """Generate optional ingress.yaml."""
        host = config.ingress_host or f"{config.app_name}.example.com"
        
        ingress = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": config.app_name,
                "namespace": config.namespace,
                "annotations": {
                    "nginx.ingress.kubernetes.io/rewrite-target": "/",
                },
            },
            "spec": {
                "rules": [
                    {
                        "host": host,
                        "http": {
                            "paths": [
                                {
                                    "path": "/",
                                    "pathType": "Prefix",
                                    "backend": {
                                        "service": {
                                            "name": config.app_name,
                                            "port": {
                                                "number": config.port,
                                            },
                                        },
                                    },
                                },
                            ],
                        },
                    },
                ],
            },
        }
        
        return yaml.dump(ingress, default_flow_style=False, sort_keys=False)
    
    def generate_configmap(self, config: K8sConfig, data: dict) -> str:
        """Generate optional configmap.yaml."""
        configmap = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"{config.app_name}-config",
                "namespace": config.namespace,
            },
            "data": data,
        }
        
        return yaml.dump(configmap, default_flow_style=False, sort_keys=False)
