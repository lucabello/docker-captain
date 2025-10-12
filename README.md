# ⚓ docker-captain

[![PyPi Release](https://img.shields.io/pypi/v/docker-captain?label=PyPi&color=blue)](https://pypi.org/project/docker-captain/)
[![GitHub Release](https://img.shields.io/github/v/release/lucabello/docker-captain?label=GitHub&color=blue)](https://github.com/lucabello/docker-captain/releases)
[![Publish to PyPi](https://github.com/lucabello/docker-captain/actions/workflows/publish.yaml/badge.svg)](https://github.com/lucabello/docker-captain/actions/workflows/publish.yaml)
![Commits Since Release](https://img.shields.io/github/commits-since/lucabello/docker-captain/latest?label=Commits%20since%20last%20release&color=darkgreen)


**docker-captain** is a friendly command-line tool that helps you manage multiple Docker Compose projects under a single folder.

---

## 🚀 Features

For a quick overview of the available commands, run `docker-captain --help`.

### 🔍 Project Auto-Detection
`docker-captain` automatically detects any subfolder containing a Docker Compose file — such as `compose.yaml`, `compose.yml`, `docker-compose.yaml`, or `docker-compose.yml`.  
It scans the folder specified in the configuration file, or passed in the `DOCKER_CAPTAIN_PROJECTS` environment variable, which you can export here:

```bash
export DOCKER_CAPTAIN_PROJECTS=/path/to/your/deployments  # takes precedence over the config file
```

Detection is purely based on the file names — if a folder contains one of those Compose files, it’s recognized as a valid “project”, taking its name from the folder.

### ⚙️ Project Management via `manage`

Use the `docker-captain manage` command to interactively select which projects should be considered *active*.
You’ll see a multi-select list of all detected projects — you can check or uncheck them using the keyboard, then confirm with Enter.

The selected projects become your *active fleet*, used by commands like `rally` and `abandon`.

### 🚢 Easy Interaction with Single Projects

Need to start or stop one project?
Use these straightforward commands:

```bash
docker-captain start calibre --detach --remove-orphans
docker-captain stop calibre --remove-orphans
docker-captain restart calibre
```

They’re thin wrappers around standard `docker compose` commands (`up`, `down`, and `restart`), but automatically use the correct compose file and folder context.

Flags:

* `-d` / `--detach`: Run containers in background.
* `--remove-orphans`: Remove orphaned containers not defined in the compose file.

### 📋 Listing Projects with `list`

See all detected projects neatly formatted in a Rich table:

```bash
docker-captain list
```

This shows:

* **Project** name
* Whether it’s **Active** (selected via `manage`)
* Whether it’s currently **Running** (`docker compose ls` is checked behind the scenes)

You can also view the compose file paths with `--verbose`:

```bash
docker-captain list --verbose
```

### ⚓ Rally and Abandon Your Fleet

Once you’ve marked projects as *active* using `manage`, you can control them all together:

* **Start all active projects:**

  ```bash
  docker-captain rally --detach
  ```
* **Stop all active projects:**

  ```bash
  docker-captain abandon
  ```

These commands behave like `start` and `stop`, but apply to every active project in one go — perfect for booting up or shutting down your entire environment.

---

## 📦 Installation

You can install `docker-captain` using `uv`, `pipx`, or plain `pip`.

```bash
# Install with
uv tool install docker-captain
pipx install docker-captain

# or try it out with
uvx docker-captain
```

---

## 🗒️ Configuration

`captain-docker` support a simple YAML config file with the following structure:

```yaml
# ~/.config/docker-captain/config.yaml (on Linux)
projects_folder: /path/to/your/deployments  # environment variable: DOCKER_CAPTAIN_PROJECTS_FOLDER
```

This configuration file can be generated interactively by running `captain-docker configure`.

---


## 🧭 Folder Structure Example

Your deployments might look like this:

```
~/Deployments/
├── calibre/
│   └── compose.yaml
├── immich/
│   ├── compose.yaml
│   └── immich.env
├── paperless-ngx/
│   ├── compose.yaml
│   └── paperless-ngx.env
└── syncthing/
    └── compose.yaml
```

Each subfolder is automatically detected as a project if it has a Compose file.

---

## 🧠 Tech Stack

| Library                                            | Purpose                      |
| -------------------------------------------------- | ---------------------------- |
| [Typer](https://typer.tiangolo.com/)               | CLI framework                |
| [Rich](https://rich.readthedocs.io/)               | Beautiful terminal output    |
| [Questionary](https://github.com/tmbo/questionary) | Interactive prompts          |
| [sh](https://amoffat.github.io/sh/)                | Simple subprocess management |
| [PyYAML](https://pyyaml.org/)                      | YAML parsing                 |

---

## 🐙 Example Workflow

```bash
# Detect and list all projects
docker-captain list

# Choose which projects are active
docker-captain manage

# Start all active projects
docker-captain rally -d
```

---

## 💡 Inspiration

I've been using `docker-compose.yaml` files to manage my home server for a while.
I found the internet is full of tools to observe docker deployments, but I couldn't find one to manage my Docker Compose files.
I wanted something simple, lightweight, and portable.

I stumbled across [jenssegers/captain](https://github.com/jenssegers/captain/), a Go project with a similar idea - a simple wrapper around `docker compose`, but only acting on one project at a time.
Given Python is my main language and the project hasn't seen any activity in 3 years, I decided to extend its scope and write `docker-captain`.

Hope this is useful to someone, happy sailing! ⛵

---

## 🔧 Development

If you want to contribute to the project, please start by opening an [issue](https://github.com/lucabello/docker-captain/issues).

You can interact with the project via `uv` and the `justfile` (from [casey/just](https://github.com/casey/just)) at the root of the repository.
Simply run `just` to show the available recipes.

```bash
# Create a virtual environment for the project
uv venv --all-groups
source .venv/bin/activate

# Linting, formatting, etc.
just  # show the list of all commands
just lint

# Run docker-captain from the local folder
uv run docker-captain
```
