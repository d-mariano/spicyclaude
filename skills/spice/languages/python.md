## Python Conventions

> Load this skill for Python implementation tasks.
> For TDD discipline, see the `test-driven-development` skill.

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

### Commands

```bash
# Testing
pytest                        # Run all
pytest -x                     # Stop on first failure
pytest -v                     # Verbose
pytest --cov=src              # With coverage
pytest -k "test_user"         # Filter by name

# Formatting
ruff format .                 # Format (or black .)
ruff check . --fix            # Lint and auto-fix

# Type checking
mypy src/                     # Check types
mypy src/ --strict            # Strict mode

# All validation
ruff check . && mypy src/ && pytest
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
