---
name: python-development
description: Python implementation with strict typing and modern patterns. Use when writing or desinging and planning to write Python code, modules, APIs, or applications. Enforces dataclasses/Pydantic over generic dicts, proper error handling, and pytest testing.
---

# Python Development

## Project Setup

**Detect existing package manager first:**

```bash
ls -la pyproject.toml poetry.lock uv.lock Pipfile* requirements.txt .venv/ 2>/dev/null
```

| Found | Use |
|-------|-----|
| `poetry.lock` | `poetry install && poetry run pytest` |
| `uv.lock` | `uv sync && uv run pytest` |
| `requirements.txt` | `source .venv/bin/activate && pip install -r requirements.txt` |
| Nothing | `uv init && uv venv && source .venv/bin/activate` |

**Never** switch package managers. **Never** install globally.

When using `uv`, avoid `uv pip install` and use commands like `uv add` and `uv sync` instead.

---

## Type System

**Avoid `Any` and generic dicts. Use structured types.**

```python
from __future__ import annotations

# ✗ AVOID
def process(data: dict[str, Any]) -> dict[str, Any]: ...

# ✓ PREFER
@dataclass(frozen=True, slots=True)
class User:
    id: int
    email: str
    name: str

def process(user: User) -> User: ...
```

| Data Origin | Use |
|-------------|-----|
| API input/output | Pydantic `BaseModel` |
| Internal objects | `@dataclass(frozen=True, slots=True)` |
| External JSON you don't control | `TypedDict` |
| Interface contracts | `Protocol` |

Details: [type-system.md](type-system.md)

---

## Core Patterns

**Pydantic for validation:**
```python
class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
```

**Dataclass for domain objects:**
```python
@dataclass(frozen=True, slots=True)
class UserId:
    value: int
```

**Protocol for DI:**
```python
class UserRepository(Protocol):
    def get(self, id: UserId) -> User | None: ...
    def save(self, user: User) -> None: ...
```

**Error handling — preserve chain, never swallow:**
```python
except httpx.HTTPError as e:
    raise ServiceError("API failed") from e

# ✗ NEVER: except Exception: pass
```

Details: [patterns.md](patterns.md)

---

## Testing

**Fixtures over setup, parametrize for variants:**

```python
@pytest.fixture
def user_service(mock_repo: Mock) -> UserService:
    return UserService(repo=mock_repo)

@pytest.mark.parametrize("email,valid", [
    ("user@example.com", True),
    ("invalid", False),
])
def test_email_validation(email: str, valid: bool) -> None:
    assert validate_email(email) == valid
```

Details: [testing.md](testing.md)

---

## Quick Reference

**Naming:** `snake_case` functions/variables, `PascalCase` classes, `SCREAMING_SNAKE` constants

**Imports:** stdlib → third-party → local

**Tooling:** `ruff` for linting + formatting

**Anti-patterns:** [anti-patterns.md](anti-patterns.md)
