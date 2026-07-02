# Patterns Reference

## Dependency Injection

```python
from typing import Protocol

class UserRepository(Protocol):
    def get(self, id: UserId) -> User | None: ...
    def save(self, user: User) -> None: ...

class UserService:
    def __init__(self, repo: UserRepository, email: EmailSender) -> None:
        self._repo = repo
        self._email = email
```

## Error Handling

```python
# Custom exceptions with context
class NotFoundError(Exception):
    def __init__(self, resource: str, id: int | str) -> None:
        self.resource, self.id = resource, id
        super().__init__(f"{resource} {id} not found")

# Always preserve chain
try:
    result = external_api.call()
except APIError as e:
    raise ServiceError("API failed") from e

# Fail fast — validate early
def process(order: Order) -> Receipt:
    if not order.items:
        raise ValidationError("items", "Order must have items")
    return _process_valid_order(order)
```

## Result Type (Optional)

```python
@dataclass(frozen=True, slots=True)
class Result(Generic[T, E]):
    _value: T | None
    _error: E | None

    @classmethod
    def ok(cls, value: T) -> Result[T, E]:
        return cls(value, None)

    @classmethod
    def err(cls, error: E) -> Result[T, E]:
        return cls(None, error)

    def unwrap(self) -> T:
        if self._value is None:
            raise ValueError(f"Error: {self._error}")
        return self._value
```

## Async Patterns

```python
# Concurrent execution
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
async def process_with_limit(items: list[T], fn: Callable, max_concurrent: int = 10) -> list[R]:
    sem = asyncio.Semaphore(max_concurrent)
    async def limited(item: T) -> R:
        async with sem:
            return await fn(item)
    return await asyncio.gather(*[limited(i) for i in items])
```

## Configuration

```python
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    debug: bool = False
    db_host: str = "localhost"
    db_port: int = 5432
    
    model_config = {"env_prefix": "APP_"}

config = Config()  # Loads from APP_DEBUG, APP_DB_HOST, etc.
```
