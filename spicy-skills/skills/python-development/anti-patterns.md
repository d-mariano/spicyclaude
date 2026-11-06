# Anti-Patterns

## Types

| ✗ Don't | ✓ Do |
|---------|------|
| `dict[str, Any]` | Dataclass, Pydantic, or TypedDict |
| `def f(x=[])` | `def f(x: list \| None = None)` |
| `type: ignore` everywhere | Fix the type issue |
| Stringly-typed: `status: str` | `status: Literal["active", "pending"]` |

## Errors

| ✗ Don't | ✓ Do |
|---------|------|
| `except:` or `except Exception:` | `except SpecificError:` |
| `except: pass` | Log or handle meaningfully |
| `raise NewError()` | `raise NewError() from e` |

## Code Organization

| ✗ Don't | ✓ Do |
|---------|------|
| `from module import *` | Explicit imports |
| Global mutable state | Dependency injection |
| Deep nesting | Early returns |
| `isinstance` chains | Pattern matching or polymorphism |

## Testing

| ✗ Don't | ✓ Do |
|---------|------|
| Tests without assertions | Explicit `assert` statements |
| Testing implementation details | Test behavior |
| Excessive mocking | Use fakes, mock only boundaries |
| Shared mutable state between tests | Fresh fixtures per test |

## Async

| ✗ Don't | ✓ Do |
|---------|------|
| `time.sleep()` in async | `await asyncio.sleep()` |
| `requests.get()` in async | `await httpx.get()` |
| Sequential awaits | `asyncio.TaskGroup` for concurrent |

## Performance

| ✗ Don't | ✓ Do |
|---------|------|
| N+1 queries | JOIN or batch queries |
| `str += ` in loop | `"".join(list)` |
| Recomputing expensive values | `@cached_property` |
