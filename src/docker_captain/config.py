"""Module to help manage configuration and data files."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields, is_dataclass
from pathlib import Path
from typing import ClassVar, Dict, List, Optional, Type, TypeVar

import questionary
import yaml
from platformdirs import user_config_dir, user_data_dir
from rich.console import Console

console = Console()
T = TypeVar("T", bound="CaptainFile")


@dataclass
class CaptainFile:
    """
    Base class that serialises dataclasses to YAML.
    Sub‑classes must be dataclasses and provide a ``DEFAULT_PATH``.
    """

    DEFAULT_PATH: ClassVar[Path]  # overridden by subclasses

    @classmethod
    def _ensure_dataclass(cls) -> None:
        if not is_dataclass(cls):
            raise TypeError(f"{cls.__name__} must be a dataclass")

    @classmethod
    def load(cls: Type[T], path: Path | None = None) -> T:
        """
        Load an instance from *path* (or ``DEFAULT_PATH``).  If the file
        cannot be read or parsed, a warning is printed and a fresh instance
        with default values is returned.
        """
        cls._ensure_dataclass()
        path = Path(path) if path is not None else cls.DEFAULT_PATH

        if not path.exists():
            return cls()

        try:
            with path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to parse {path}: {e}[/yellow]")
            return cls()

        # Keep only fields defined on the dataclass
        field_names = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in data.items() if k in field_names}
        return cls(**filtered)

    def save(self, path: Path | None = None) -> None:
        """
        Write the instance to *path* (or ``DEFAULT_PATH``) as YAML.
        The parent directory is created automatically.  Errors are
        reported with a console warning but not re‑raised.
        """
        self.__class__._ensure_dataclass()
        path = Path(path) if path is not None else self.__class__.DEFAULT_PATH
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with path.open("w", encoding="utf-8") as f:
                yaml.safe_dump(
                    asdict(self),
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                )
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to write {path}: {e}[/yellow]")


@dataclass
class CaptainConfig(CaptainFile):
    """Data model of the docker-captain configuration file."""

    DEFAULT_PATH: ClassVar[Path] = (
        Path(user_config_dir(appname="docker-captain", appauthor=False)) / "config.yaml"
    )
    ENVIROMENT: ClassVar[Dict] = {"projects_folder": "DOCKER_CAPTAIN_PROJECTS_FOLDER"}

    projects_folder: Optional[Path] = field(
        default=None, metadata={"env": "DOCKER_CAPTAIN_PROJECTS_FOLDER"}
    )

    @classmethod
    def interactive(cls) -> None:
        """Interactively write a configuration file."""
        config = cls()
        try:
            config.projects_folder = questionary.text(
                "projects_folder", instruction="(absolute path)"
            ).ask()
        except Exception as e:
            console.print(f"[red]Error when processing user input: {e}[/red]")
            exit(code=1)
        console.print(f"[green]Saving configuration to {config.DEFAULT_PATH}[/green]")
        config.save()


@dataclass
class CaptainData(CaptainFile):
    """Data model of the docker-captain data."""

    DEFAULT_PATH: ClassVar[Path] = (
        Path(user_data_dir(appname="docker-captain", appauthor=False)) / "data.yaml"
    )

    active_projects: List[str] = field(default_factory=list)
