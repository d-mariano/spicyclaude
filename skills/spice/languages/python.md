## Python Conventions

> Load this skill for Python implementation tasks.
> For TDD discipline, see the `test-driven-development` skill.

---

### Project Setup (CRITICAL)

#### Detect Existing Package Manager FIRST

**Before doing anything, detect the existing setup and use it:**

```bash
# Check what exists
ls -la pyproject.toml poetry.lock uv.lock Pipfile Pipfile.lock requirements.txt .venv/ venv/ 2>/dev/null
```

| Found | Package Manager | Use These Commands |
|-------|-----------------|-------------------|
| `poetry.lock` | Poetry | `poetry install`, `poetry run pytest` |
| `uv.lock` | uv | `uv sync`, `uv run pytest` |
| `Pipfile.lock` | Pipenv | `pipenv install`, `pipenv run pytest` |
| `requirements.txt` + `.venv/` | pip + venv | `source .venv/bin/activate`, `pip install` |
| `pyproject.toml` only | Check for `[tool.poetry]` → Poetry, else try `uv sync` |
| Nothing | New project — use `uv init` |

#### Respect Existing Environment

**NEVER switch package managers on an existing project.** Use what's already there.

```bash
# ✅ CORRECT: Detect and use existing
if [ -f "poetry.lock" ]; then
    poetry install
    poetry run pytest
elif [ -f "uv.lock" ]; then
    uv sync
    uv run pytest
elif [ -f "Pipfile.lock" ]; then
    pipenv install
    pipenv run pytest
elif [ -f "requirements.txt" ]; then
    # Activate existing venv or create one
    [ -d ".venv" ] && source .venv/bin/activate || (python -m venv .venv && source .venv/bin/activate)
    pip install -r requirements.txt
    pytest
fi

# ❌ WRONG: Ignore existing setup
uv init  # Don't do this if poetry.lock exists!
```

#### New Projects Only: Use `uv`

**Only for NEW projects with no existing package manager:**

```bash
# Verify nothing exists first
[ ! -f pyproject.toml ] && [ ! -f requirements.txt ] && [ ! -f Pipfile ] && [ ! -f poetry.lock ]

# Then initialize with uv
uv init
uv venv
source .venv/bin/activate
uv add pydantic httpx
uv add --dev pytest pytest-asyncio ruff mypy
```

#### NEVER Do This

```bash
# ❌ NEVER install globally (without active venv)
pip install package-name

# ❌ NEVER ignore existing package manager
uv init  # when poetry.lock already exists

# ❌ NEVER mix package managers
poetry add package && uv add another-package
```

---

### Commands by Package Manager

#### Poetry Projects
```bash
poetry install                 # Install deps
poetry add package-name        # Add dependency
poetry add --group dev pytest  # Add dev dependency
poetry run pytest              # Run tests
poetry run mypy src/           # Type check
poetry run ruff check .        # Lint
```

#### uv Projects
```bash
uv sync                        # Install deps
uv add package-name            # Add dependency  
uv add --dev pytest            # Add dev dependency
uv run pytest                  # Run tests
uv run mypy src/               # Type check
uv run ruff check .            # Lint
```

#### pip/venv Projects
```bash
source .venv/bin/activate      # Activate venv (or: . venv/bin/activate)
pip install -r requirements.txt # Install deps
pip install package-name       # Add dependency (update requirements.txt!)
pytest                         # Run tests
mypy src/                      # Type check
ruff check .                   # Lint
```

#### Pipenv Projects
```bash
pipenv install                 # Install deps
pipenv install package-name    # Add dependency
pipenv install --dev pytest    # Add dev dependency
pipenv run pytest              # Run tests
pipenv run mypy src/           # Type check
pipenv run ruff check .        # Lint
```

---

### Type System

#### Type Hints (Required)

All function signatures must have complete type hints:

```python
from __future__ import annotations

def process_user(
    user_id: int, 
    options: dict[str, str] | None = None
) -> User:
    ...
```

**Rules:**
- Use `from __future__ import annotations` for forward refs
- Modern syntax: `list[str]` not `List[str]`, `str | None` not `Optional[str]`
- Target `mypy --strict` compatibility
- Explicit return types always

#### Common Patterns

```python
# Protocol for interfaces (dependency inversion)
from typing import Protocol

class Repository(Protocol):
    def get(self, id: int) -> Model | None: ...
    def save(self, model: Model) -> None: ...

# TypedDict for structured dicts (external data)
from typing import TypedDict

class UserData(TypedDict):
    name: str
    email: str
    age: int | None

# Dataclass for internal data objects
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class UserId:
    value: int
```

---

### Code Style

#### Formatting (Automated)
- **black** — Code formatting (line length 88)
- **isort** — Import sorting (black profile)
- **ruff** — Linting (replaces flake8, pylint)

#### Naming
- `snake_case` — functions, variables, modules
- `PascalCase` — classes, type aliases
- `SCREAMING_SNAKE_CASE` — constants
- `_private` — leading underscore for private

#### Import Order
```python
# Standard library
from collections.abc import Sequence
from pathlib import Path

# Third-party
import httpx
from pydantic import BaseModel

# Local
from .models import User
from .utils import validate
```

---

### Patterns

#### Data Validation (Pydantic)

```python
from pydantic import BaseModel, EmailStr, Field, field_validator

class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    age: int | None = Field(default=None, ge=0, le=150)

    @field_validator('name')
    @classmethod
    def normalize_name(cls, v: str) -> str:
        return v.strip().title()
```

#### Error Handling

```python
# Fail fast — specific exceptions, preserve chain
try:
    result = external_api.fetch(id)
except httpx.HTTPError as e:
    raise ServiceUnavailableError(f"API failed for {id}") from e

# Custom exceptions with context
class UserNotFoundError(Exception):
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id
        super().__init__(f"User {user_id} not found")
```

**Don't:**
```python
# Silent failure — NEVER DO THIS
try:
    result = risky_operation()
except Exception:
    result = None
```

#### Dependency Injection

```python
from typing import Protocol

class UserRepository(Protocol):
    def get(self, user_id: int) -> User | None: ...
    def save(self, user: User) -> None: ...

class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    def activate(self, user_id: int) -> User:
        user = self._repo.get(user_id)
        if user is None:
            raise UserNotFoundError(user_id)
        user.active = True
        self._repo.save(user)
        return user
```

#### Async Patterns

```python
import asyncio
from collections.abc import AsyncIterator

async def fetch_all(ids: list[int]) -> list[Result]:
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch_one(id)) for id in ids]
    return [task.result() for task in tasks]

# Async context manager
async def get_connection() -> AsyncIterator[Connection]:
    conn = await pool.acquire()
    try:
        yield conn
    finally:
        await pool.release(conn)
```

---

### Testing

#### Framework
- **pytest** — Test framework
- **pytest-asyncio** — Async testing
- **pytest-mock** — Mocking via `mocker` fixture

#### Project Structure
```
src/
└── myapp/
    ├── __init__.py
    ├── service.py
    └── repository.py
tests/
├── conftest.py           # Shared fixtures
├── unit/
│   └── test_service.py
├── integration/
│   └── test_api.py
└── fixtures/
    └── users.json
```

#### Fixtures Over Setup

```python
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_repo() -> Mock:
    repo = Mock(spec=UserRepository)
    repo.get.return_value = User(id=1, name="Test", active=False)
    return repo

@pytest.fixture
def user_service(mock_repo: Mock) -> UserService:
    return UserService(repo=mock_repo)

def test_activate_user_sets_active_true(user_service: UserService) -> None:
    result = user_service.activate(1)
    assert result.active is True
```

#### Parametrized Tests

```python
import pytest

@pytest.mark.parametrize("email,valid", [
    ("user@example.com", True),
    ("user@test.co.uk", True),
    ("invalid", False),
    ("@missing.com", False),
    ("spaces @test.com", False),
])
def test_email_validation(email: str, valid: bool) -> None:
    result = validate_email(email)
    assert result == valid
```

#### Async Tests

```python
import pytest

@pytest.mark.asyncio
async def test_fetch_user_returns_user() -> None:
    service = UserService(FakeRepository())
    result = await service.fetch_user(1)
    assert result.id == 1
```

---

### Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Mutable default args `def f(x=[])` | `def f(x=None): x = x or []` |
| Bare `except:` | `except SpecificError:` |
| `%` or `.format()` | f-strings |
| `from module import *` | Explicit imports |
| Global mutable state | Dependency injection |
| `isinstance` chains | Polymorphism or match |
| `type: ignore` everywhere | Fix the type issue |
| Nested try/except | Single handler, re-raise |

---

### Quick Reference

```python
# Modern Python patterns
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from pydantic import BaseModel

# Pattern matching (3.10+)
match command:
    case ["quit"]:
        return
    case ["load", filename]:
        load_file(filename)
    case _:
        print("Unknown command")

# Structural pattern matching with types
match user:
    case User(role="admin"):
        grant_admin_access()
    case User(role="user", verified=True):
        grant_user_access()
    case _:
        deny_access()
```
