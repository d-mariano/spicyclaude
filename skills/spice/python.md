## Python Conventions

> Load this resource for Python implementation tasks.
> For TDD discipline, see the `test-driven-development` skill.

---

### Type System

#### Type Hints (Required)

All function signatures must have complete type hints:

```python
from __future__ import annotations

def process_user(user_id: int, options: dict[str, str] | None = None) -> User:
    ...
```

**Rules:**
- Use `from __future__ import annotations` for forward refs
- Modern syntax: `list[str]` not `List[str]`, `str | None` not `Optional[str]`
- Target `mypy --strict` compatibility

#### Common Patterns

```python
# Protocol for interfaces
from typing import Protocol

class Repository(Protocol):
    def get(self, id: int) -> Model | None: ...
    def save(self, model: Model) -> None: ...

# TypedDict for structured dicts
from typing import TypedDict

class UserData(TypedDict):
    name: str
    email: str
    age: int | None
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

#### Imports Order
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

#### Data Structures

```python
# Immutable data objects
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class UserId:
    value: int

# Validated input
from pydantic import BaseModel, field_validator

class CreateUserRequest(BaseModel):
    email: str
    name: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if '@' not in v:
            raise ValueError('Invalid email')
        return v.lower()
```

#### Error Handling

```python
# Fail fast — specific exceptions, preserve chain
try:
    result = external_api.fetch(id)
except httpx.HTTPError as e:
    raise ServiceUnavailableError(f"API failed for {id}") from e

# Don't swallow errors silently
# BAD:
try:
    result = risky_operation()
except Exception:
    result = None  # Silent failure — DON'T DO THIS
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

---

### Testing

#### Framework
- **pytest** — Test framework
- **pytest-asyncio** — Async testing
- **pytest-mock** — Mocking

#### Structure
```
tests/
├── conftest.py          # Shared fixtures
├── unit/
│   └── test_*.py
├── integration/
│   └── test_*.py
└── fixtures/
    └── *.json
```

#### Fixtures Over Setup

```python
import pytest

@pytest.fixture
def user_service(mock_repo: MockUserRepo) -> UserService:
    return UserService(repo=mock_repo)

def test_activate_user(user_service: UserService) -> None:
    result = user_service.activate(1)
    assert result.active is True
```

---

### Commands

```bash
# Testing
poetry run pytest                 # Run all
poetry run pytest -x              # Stop on first failure
poetry run pytest --cov=src       # With coverage

# Formatting
poetry run black .
poetry run isort .
poetry run ruff check . --fix

# Type checking
poetry run mypy src
```

---

### Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Mutable default args | Use `None` with conditional |
| Bare `except:` | Specify exception type |
| `%` or `.format()` | Use f-strings |
| `from module import *` | Explicit imports |
| Global mutable state | Dependency injection |
| `isinstance` for flow control | Polymorphism |
