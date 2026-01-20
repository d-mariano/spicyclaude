---
name: python-development
description: Python implementation with strict typing and modern patterns. Use when writing Python code, modules, APIs, or applications. Enforces dataclasses/Pydantic over generic dicts, proper error handling, and pytest testing.
---

# Python Development

## Project Setup

**Detect existing package manager first:**
```bash
ls -la pyproject.toml poetry.lock uv.lock Pipfile* requirements.txt .venv/ 2>/dev/null
```

| Found | Use |
|-------|-----|
| `uv.lock` | `uv sync && uv run pytest` |
| `poetry.lock` | `poetry install && poetry run pytest` |
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

### Type Selection

| Data Origin | Use |
|-------------|-----|
| API input/output | Pydantic `BaseModel` |
| Internal objects | `@dataclass(frozen=True, slots=True)` |
| External JSON you don't control | `TypedDict` |
| Interface contracts | `Protocol` |

### Pydantic (External Data)

```python
from pydantic import BaseModel, Field, EmailStr, field_validator

class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    roles: list[str] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def normalize(cls, v: str) -> str:
        return v.strip().title()
```

### Dataclass (Domain Objects)

```python
@dataclass(frozen=True, slots=True)
class UserId:
    value: int

@dataclass(frozen=True, slots=True)
class User:
    id: UserId
    email: str
    active: bool = False

    def activate(self) -> User:
        return User(id=self.id, email=self.email, active=True)
```

### Protocol (Interfaces)

```python
from typing import Protocol

class UserRepository(Protocol):
    def get(self, id: UserId) -> User | None: ...
    def save(self, user: User) -> None: ...

# Any class with matching methods satisfies the Protocol
```

### Other Useful Types

`Literal["pending", "active"]` for constrained strings, `NewType("UserId", int)` to prevent mixing IDs.

---

## Error Handling

```python
# Custom exceptions with context
class NotFoundError(Exception):
    def __init__(self, resource: str, id: int | str) -> None:
        self.resource, self.id = resource, id
        super().__init__(f"{resource} {id} not found")

# Always preserve exception chain
try:
    result = api.fetch(id)
except httpx.HTTPError as e:
    raise ServiceError("API failed") from e

# Fail fast — validate early
def process(order: Order) -> Receipt:
    if not order.items:
        raise ValidationError("Order must have items")
    return _process_valid_order(order)
```

**Never** silently swallow: `except Exception: pass`

---

## Async Patterns

```python
# Concurrent execution with TaskGroup
async def fetch_dashboard(user_id: UserId) -> Dashboard:
    async with asyncio.TaskGroup() as tg:
        user = tg.create_task(get_user(user_id))
        orders = tg.create_task(get_orders(user_id))
    return Dashboard(user.result(), orders.result())

# Async context manager
@asynccontextmanager
async def get_connection() -> AsyncIterator[Connection]:
    conn = await pool.acquire()
    try:
        yield conn
    finally:
        await pool.release(conn)

# Rate-limited concurrency
async def process_batch(items: list[T], fn: Callable, limit: int = 10) -> list[R]:
    sem = asyncio.Semaphore(limit)
    async def limited(item: T) -> R:
        async with sem:
            return await fn(item)
    return await asyncio.gather(*[limited(i) for i in items])
```

---

## Testing

### Fixtures

```python
@pytest.fixture
def mock_repo() -> Mock:
    repo = Mock(spec=UserRepository)
    repo.get.return_value = User(id=UserId(1), email="test@example.com", name="Test")
    return repo

@pytest.fixture
def user_service(mock_repo: Mock) -> UserService:
    return UserService(repo=mock_repo)

# Factory fixture for flexible creation
@pytest.fixture
def user_factory() -> Callable[..., User]:
    def _create(id: int = 1, **kwargs) -> User:
        return User(id=UserId(id), email=kwargs.get("email", "test@example.com"), **kwargs)
    return _create
```

### Fake Over Mock (for complex logic)

```python
@dataclass
class FakeUserRepository:
    _users: dict[UserId, User] = field(default_factory=dict)

    def get(self, id: UserId) -> User | None:
        return self._users.get(id)

    def save(self, user: User) -> None:
        self._users[user.id] = user
```

### Parametrized Tests

```python
@pytest.mark.parametrize("email,valid", [
    ("user@example.com", True),
    ("user@test.co.uk", True),
    ("invalid", False),
    ("@missing.com", False),
])
def test_email_validation(email: str, valid: bool) -> None:
    assert validate_email(email) == valid
```

### Async Tests

```python
@pytest.mark.asyncio
async def test_fetch_user() -> None:
    service = UserService(FakeRepository())
    result = await service.fetch(UserId(1))
    assert result.id == UserId(1)
```

### Testing Exceptions

```python
def test_raises_not_found() -> None:
    with pytest.raises(NotFoundError) as exc:
        service.get_user(UserId(999))
    assert exc.value.id == 999
```

---

## Anti-Patterns

| ✗ Don't | ✓ Do |
|---------|------|
| `dict[str, Any]` | Dataclass, Pydantic, or TypedDict |
| `def f(x=[])` | `def f(x: list \| None = None)` |
| `except:` / `except Exception: pass` | `except SpecificError:` + handle |
| `raise NewError()` | `raise NewError() from e` |
| `from module import *` | Explicit imports |
| Global mutable state | Dependency injection |
| `time.sleep()` in async | `await asyncio.sleep()` |
| `requests.get()` in async | `await httpx.get()` |
| Sequential awaits | `asyncio.TaskGroup` for concurrent |
| Excessive mocking | Fakes for complex logic |
| Tests without assertions | Explicit `assert` statements |