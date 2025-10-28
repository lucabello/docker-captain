"""Module to help wrapping 'docker compose' commands."""

import json
from pathlib import Path
from typing import List, Literal

import sh
from rich.console import Console

console = Console()


class DockerCompose:
    """Wrapper around 'docker compose' commands."""

    @staticmethod
    def get_running_projects() -> List[str]:
        """Return a list of running docker compose projects using `docker compose ls`.

        Returns:
            List[str]: Subset of the passed projects that are currently running.
        """
        try:
            result = sh.docker.compose.ls(format="json", _ok_code=[0, 1])  # pyright: ignore[reportAttributeAccessIssue]
            data = json.loads(str(result))
            running = []
            for item in data:
                name = item.get("Name")
                if name and item.get("Status", "").lower().startswith("running"):
                    running.append(name)
            return running
        except sh.CommandNotFound as e:
            console.print(f"[red][bold]Error:[/bold] '{e}' command not found.[/red]")
            exit(code=1)
        except Exception as e:
            console.print(f"[yellow]Warning: could not determine running projects ({e})[/yellow]")
            return []

    @staticmethod
    def up(compose_file: Path, **kwargs) -> int:
        """Run 'docker compose up' with the specified **kwargs.

        Args:
            compose_file (Path): Path to the compose YAML file.
            **kwargs (Dict): Optional arguments to pass directly to docker compose.

        Returns:
            int: Exit code of the docker command.

        """
        return DockerCompose._docker_compose_run(compose_file=compose_file, action="up", **kwargs)

    @staticmethod
    def down(compose_file: Path, **kwargs) -> int:
        """Run 'docker compose down' with the specified **kwargs.

        Args:
            compose_file (Path): Path to the compose YAML file.
            **kwargs (Dict): Optional arguments to pass directly to docker compose.

        Returns:
            int: Exit code of the docker command.

        """
        return DockerCompose._docker_compose_run(
            compose_file=compose_file, action="down", **kwargs
        )

    @staticmethod
    def restart(compose_file: Path, **kwargs) -> int:
        """Run 'docker compose restart' with the specified **kwargs.

        Args:
            compose_file (Path): Path to the compose YAML file.
            **kwargs (Dict): Optional arguments to pass directly to docker compose.

        Returns:
            int: Exit code of the docker command.

        """
        return DockerCompose._docker_compose_run(
            compose_file=compose_file, action="restart", **kwargs
        )

    @staticmethod
    def _docker_compose_run(
        compose_file: Path,
        action: Literal["up", "down", "restart"],
        **kwargs,
    ) -> int:
        """Internal wrapper to run docker compose command via sh.docker.compose.


        Args:
            compose_file (Path): Path to the compose YAML file.
            action (str): 'up' or 'down', to indicate which docker compose command to run.
            **kwargs (Dict): Optional arguments to pass directly to docker compose.

        Returns:
            int: Exit code of the docker command.

        """
        console.rule(f"[bold blue]{action.upper()} {compose_file.parent.name}[/bold blue]")
        try:
            docker_compose = sh.Command("docker").bake("compose").bake(file=compose_file)
            docker_compose(action, **kwargs, _fg=True)
            console.print(
                f":white_check_mark: [green]{action} succeeded for {compose_file.parent.name}[/green]"
            )
            return 0
        except sh.CommandNotFound as e:
            console.print(f"[red]'{e}' command not found.[/red]")
            return 1
        except sh.ErrorReturnCode as e:
            console.print(f"[red]Command failed with exit code {e.exit_code}[/red]")
            return int(e.exit_code)
        except Exception as e:
            console.print(f"[red]Error executing docker compose: {e}[/red]")
            return 2
