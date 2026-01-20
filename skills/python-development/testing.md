# Testing Reference

## Structure

```
src/myapp/
tests/
    conftest.py       # Shared fixtures
    unit/
    integration/
```

## Fixtures

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
    def _create(id: int = 1, email: str = "test@example.com", **kwargs) -> User:
        return User(id=UserId(id), email=email, **kwargs)
    return _create

# Scoped fixtures
@pytest.fixture(scope="module")
def database() -> Iterator[Database]:
    db = Database.connect()
    yield db
    db.disconnect()
```

## Parametrized Tests

```python
@pytest.mark.parametrize("email,valid", [
    ("user@example.com", True),
    ("invalid", False),
])
def test_email_validation(email: str, valid: bool) -> None:
    assert validate_email(email) == valid
```

## Async Tests

```python
@pytest.mark.asyncio
async def test_fetch_user() -> None:
    service = UserService(FakeRepository())
    result = await service.fetch(UserId(1))
    assert result.id == UserId(1)
```

## Test Doubles

```python
# Mock with spec (catches typos)
mock_repo = Mock(spec=UserRepository)

# AsyncMock for async methods
async_repo = AsyncMock(spec=UserRepository)

# Fake implementation (preferred for complex logic)
@dataclass
class FakeUserRepository:
    _users: dict[UserId, User] = field(default_factory=dict)
    
    def get(self, id: UserId) -> User | None:
        return self._users.get(id)
    
    def save(self, user: User) -> None:
        self._users[user.id] = user
```

## Testing Exceptions

```python
def test_raises_not_found() -> None:
    with pytest.raises(NotFoundError) as exc:
        service.get_user(UserId(999))
    assert exc.value.id == 999
```

## pyproject.toml

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = ["-v", "--strict-markers"]
```
