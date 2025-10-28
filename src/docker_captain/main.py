"""
A friendly CLI tool for managing multiple Docker Compose projects.

docker-captain detects projects automatically, lets you mark them as active,
and provides simple commands to start, stop, restart, or list your deployments
— individually or all at once.
"""

from __future__ import annotations

from typing import List

import questionary
import typer
from questionary import Choice
from rich import box
from rich.console import Console
from rich.table import Table

from docker_captain.config import CaptainConfig, CaptainData
from docker_captain.docker import DockerCompose
from docker_captain.projects import CaptainProject

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

app = typer.Typer(no_args_is_help=True)
console = Console()

# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


@app.command(rich_help_panel="Manage")
def list(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show compose file paths."),
) -> None:
    """List all discovered projects and show which ones are active and running.

    Args:
        verbose (bool): If True, also show the compose file path.
    """
    projects_folder = CaptainProject.projects_folder()
    projects = CaptainProject.discover_projects()
    captain_data: CaptainData = CaptainData.load()
    running_projects: List[str] = DockerCompose.get_running_projects()

    table = Table(title=f"Projects in {projects_folder}", box=box.SIMPLE_HEAVY)
    table.add_column("Project", no_wrap=True)
    table.add_column("Active", justify="center")
    table.add_column("Running", justify="center")

    if verbose:
        table.add_column("Compose File")

    for name, compose_path in projects.items():
        active = "✓" if name in captain_data.active_projects else ""
        running = "✓" if name in running_projects else ""
        row = [name, active, running]
        if verbose:
            row.append(str(compose_path))
        table.add_row(*row)

    console.print(table)


@app.command(rich_help_panel="Manage")
def manage() -> None:
    """Interactively select which projects are active."""
    projects_folder = CaptainProject.projects_folder()
    projects = CaptainProject.discover_projects()
    names = sorted(projects.keys())
    captain_data: CaptainData = CaptainData.load()

    if not names:
        console.print(f"[yellow]No projects found in {projects_folder}.[/yellow]")
        raise typer.Exit(code=1)

    # Build choices with checkmarks for active projects
    choices = [
        Choice(title=n, value=n, checked=(n in captain_data.active_projects)) for n in names
    ]

    answer = questionary.checkbox(
        "Select active projects (space to toggle, enter to confirm):",
        choices=choices,
    ).ask()

    if answer is None:
        console.print("[yellow]Aborted (no changes made).[/yellow]")
        raise typer.Exit(code=0)

    captain_data.active_projects = sorted(answer)
    captain_data.save()
    console.print(
        f"[green]Saved {len(captain_data.active_projects)} active project(s) to {captain_data.DEFAULT_PATH}[/green]"
    )


@app.command()
def start(
    project: str = typer.Argument(..., help="Project folder name (e.g. calibre)"),
    detach: bool = typer.Option(False, "-d", "--detach", help="Run `docker compose up --detach`"),
    remove_orphans: bool = typer.Option(
        False, "--remove-orphans", help="Include --remove-orphans"
    ),
) -> None:
    """Start a single project using `docker compose up`."""
    projects = CaptainProject.discover_projects()
    compose_file = CaptainProject.require_project_exists(project, projects)
    rc = DockerCompose.up(
        compose_file=compose_file,
        detach=detach,
        remove_orphans=remove_orphans,
    )
    raise typer.Exit(code=rc)


@app.command()
def stop(
    project: str = typer.Argument(..., help="Project folder name (e.g. calibre)"),
    remove_orphans: bool = typer.Option(
        False, "--remove-orphans", help="Include --remove-orphans"
    ),
) -> None:
    """Stop a single project using `docker compose down`."""
    projects = CaptainProject.discover_projects()
    compose_file = CaptainProject.require_project_exists(project, projects)
    rc = DockerCompose.down(
        compose_file=compose_file,
        remove_orphans=remove_orphans,
    )
    raise typer.Exit(code=rc)


@app.command()
def restart(
    project: str = typer.Argument(..., help="Project folder name (e.g. calibre)"),
) -> None:
    """Restart a single project using `docker compose restart`."""
    projects = CaptainProject.discover_projects()
    compose_file = CaptainProject.require_project_exists(project, projects)
    rc = DockerCompose.restart(compose_file=compose_file)
    raise typer.Exit(code=rc)


@app.command()
def rally(
    remove_orphans: bool = typer.Option(
        False, "--remove-orphans", help="Include --remove-orphans"
    ),
) -> None:
    """Start all active projects."""
    projects = CaptainProject.discover_projects()
    captain_data = CaptainData.load()

    if not captain_data.active_projects:
        console.print(
            f"[yellow]No active projects found in {captain_data.DEFAULT_PATH}. Run `docker-captain manage` first.[/yellow]"
        )
        raise typer.Exit(code=0)

    exit_code = 0
    for name in captain_data.active_projects:
        if name not in projects:
            console.print(f"[red]Skipping {name}: project not found.[/red]")
            exit_code = exit_code or 1
            continue
        rc = DockerCompose.up(
            compose_file=projects[name], detach=True, remove_orphans=remove_orphans
        )
        exit_code = exit_code or rc
    raise typer.Exit(code=exit_code)


@app.command()
def abandon(
    remove_orphans: bool = typer.Option(
        False, "--remove-orphans", help="Include --remove-orphans"
    ),
) -> None:
    """Stop all active projects."""
    projects = CaptainProject.discover_projects()
    captain_data = CaptainData.load()

    if not captain_data.active_projects:
        console.print(
            f"[yellow]No active projects found in {captain_data.DEFAULT_PATH}. Run `docker-captain manage` first.[/yellow]"
        )
        raise typer.Exit(code=0)

    exit_code = 0
    for name in captain_data.active_projects:
        if name not in projects:
            console.print(f"[red]Skipping {name}: project not found.[/red]")
            exit_code = exit_code or 1
            continue
        rc = DockerCompose.down(compose_file=projects[name], remove_orphans=remove_orphans)
        exit_code = exit_code or rc
    raise typer.Exit(code=exit_code)


@app.command(rich_help_panel="Utils and Configs")
def configure() -> None:
    """Interactively write a configuration file."""
    CaptainConfig.interactive()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    app()
