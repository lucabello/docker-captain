"""Module to help manage configuration and data files."""

# captain_file.py
from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields, is_dataclass
from pathlib import Path
from typing import ClassVar, List, Type, TypeVar

import yaml
from platformdirs import user_config_dir, user_data_dir
from rich.console import Console

T = TypeVar("T", bound="CaptainFile")
console = Console()


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
            return cls()  # type: ignore[arg-type]

        try:
            with path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except Exception as e:  # pragma: no cover
            console.print(f"[yellow]Warning: Failed to parse {path}: {e}[/yellow]")
            return cls()  # type: ignore[arg-type]

        # Keep only fields defined on the dataclass
        field_names = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in data.items() if k in field_names}
        return cls(**filtered)  # type: ignore[arg-type]

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
        except Exception as e:  # pragma: no cover
            console.print(f"[yellow]Warning: Failed to write {path}: {e}[/yellow]")


@dataclass
class CaptainConfig(CaptainFile):
    DEFAULT_PATH: ClassVar[Path] = (
        Path(user_config_dir(appname="docker-captain", appauthor=False)) / "config.yaml"
    )

    theme: str = "light"
    auto_update: bool = True
    recent_files: List[Path] = field(default_factory=list)


@dataclass
class CaptainData(CaptainFile):
    DEFAULT_PATH: ClassVar[Path] = (
        Path(user_data_dir(appname="docker-captain", appauthor=False)) / "data.yaml"
    )

    active_projects: List[str] = field(default_factory=list)
