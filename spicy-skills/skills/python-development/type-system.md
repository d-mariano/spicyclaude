# Type System Reference

## Decision Tree

```
External data needing validation? → Pydantic BaseModel
Internal domain object?          → @dataclass(frozen=True, slots=True)  
Dict from external API?          → TypedDict
Behavior contract for DI?        → Protocol
```

## Pydantic (External Data)

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

# Nested models, serialization
class Company(BaseModel):
    name: str
    address: Address
    
    model_config = {"from_attributes": True}  # Allow ORM objects

company.model_dump()      # To dict
company.model_dump_json() # To JSON
```

## Dataclasses (Domain Objects)

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

Options: `frozen=True` (immutable), `slots=True` (memory efficient), `kw_only=True` (keyword args only)

## TypedDict (External JSON)

```python
from typing import TypedDict, NotRequired

class UserData(TypedDict):
    id: int
    name: str
    age: NotRequired[int]  # Optional key
```

## Protocol (Interfaces)

```python
from typing import Protocol

class Repository(Protocol):
    def get(self, id: int) -> Model | None: ...
    def save(self, model: Model) -> None: ...

# Any class with matching methods satisfies the Protocol
```

## Useful Patterns

```python
# Literal for constrained strings
Status = Literal["pending", "active", "suspended"]

# NewType for semantic distinction
UserId = NewType("UserId", int)
OrderId = NewType("OrderId", int)

# TypeGuard for narrowing
def is_string_list(val: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(x, str) for x in val)
```

## When Types Don't Cooperate

**Never reach for `# type: ignore` first.** It silences the checker without fixing the underlying problem. Work the ladder:

1. **Import the correct type from the third-party library.** Use aliased imports to avoid name collisions: `from lib import Foo as LibFoo`.
2. **If the type doesn't exist publicly**, check whether the library exports a `TypedDict`, `Protocol`, or base class you should use instead.
3. **Only as a last resort**, use `# type: ignore[<error-code>]` when the library's own stubs are genuinely wrong — and add a comment explaining why.

When typing errors surface, work backwards before suppressing:

- A typing incompatibility is often a **red flag for a deeper code issue** — wrong abstraction, mixed concerns, or a contract that doesn't hold.
- An **incorrect type hint** may have been assigned to a variable or function definition; fix the hint rather than the call site.
