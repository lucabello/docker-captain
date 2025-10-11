import os
from pathlib import Path
from typing import Dict, List, Optional

import typer
from rich.console import Console

from docker_captain.config import CaptainConfig

console = Console()


class CaptainProject:
    @staticmethod
    def projects_folder() -> Path:
        """Get the root folder of the projects.

        Either parse it from the environment variable (if provided), or from
        the configuration file.
        """
        captain_config = CaptainConfig.load()
        folder = (
            os.getenv(CaptainConfig.ENVIROMENT["projects_folder"])
            or captain_config.projects_folder
        )
        if not folder:
            console.print(
                f"[bold red]Error:[/bold red] Please set the path containing your Docker Compose projects.\n"
                f"Either add it to the {CaptainConfig.DEFAULT_PATH} file, or set with:\n\n"
                f"    export {CaptainConfig.ENVIROMENT['projects_folder']}=/path/to/your/deployments\n"
            )
            exit(code=1)
        folder = Path(folder)
        if not folder.is_absolute():
            console.print(
                f"[bold red]Error:[/bold red] The configured projects folder {folder} "
                "is not an absolute path."
            )
            exit(code=2)
        if not folder.exists():
            console.print(
                f"[bold red]Error:[/bold red] The configured projects folder {folder} "
                "does not exist."
            )
            exit(code=3)
        return folder

    @staticmethod
    def discover_projects(root: Optional[Path] = None) -> Dict[str, Path]:
        """Discover projects that contain a valid docker compose file.

        Args:
            root (Path): The root directory containing deployment folders.

        Returns:
            Dict[str, Path]: Mapping from project name to compose file path.
        """
        COMPOSE_FILENAMES: List[str] = [
            "compose.yaml",
            "compose.yml",
            "docker-compose.yaml",
            "docker-compose.yml",
        ]
        projects: Dict[str, Path] = {}
        root = root or CaptainProject.projects_folder()
        if not root.exists():
            return projects
        for child in sorted(root.iterdir()):
            if not child.is_dir():
                continue
            for fname in COMPOSE_FILENAMES:
                candidate = child / fname
                if candidate.exists() and candidate.is_file():
                    projects[child.name] = candidate
                    break
        return projects

    @staticmethod
    def require_project_exists(project: str, projects: Dict[str, Path]) -> Path:
        """Ensure the given project exists among discovered ones.

        Args:
            project (str): Project name.
            projects (Dict[str, Path]): Mapping of available projects.

        Returns:
            Path: Path to the compose file.

        Raises:
            typer.Exit: If the project does not exist.
        """
        if project not in projects:
            console.print(f"[red]No such project: {project}[/red]")
            raise typer.Exit(code=2)
        return projects[project]
