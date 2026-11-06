# Test Doubles — When and How to Use Them

Test doubles replace real dependencies in tests. Choosing the right kind — and knowing
when NOT to use one — is the difference between a useful test suite and a brittle one.

## Decision Framework

**Use real implementations when:**
- The dependency is fast, deterministic, and has no side effects
- The dependency is a pure function or value object
- You're testing integration between components (integration tests)

**Use test doubles when:**
- The dependency is slow (network, disk, external API)
- The dependency is non-deterministic (system clock, random)
- The dependency has side effects (sends email, charges payment, writes to DB)
- You need to simulate error conditions (timeouts, failures)

**The boundary rule:** Only double things at the boundary of your system. HTTP clients,
database connections, message queues, file systems, third-party APIs — these get doubled.
Internal classes and business logic do not.

---

## Types of Test Doubles

### Fakes — working implementations with shortcuts

Fakes have real behavior but take shortcuts unsuitable for production (in-memory
database, local file store instead of S3).

```python
class InMemoryUserRepository:
    def __init__(self):
        self._users = {}

    def save(self, user):
        self._users[user.id] = user

    def find_by_email(self, email):
        return next((u for u in self._users.values() if u.email == email), None)
```

```typescript
class InMemoryUserRepository implements UserRepository {
  private users = new Map<string, User>();

  save(user: User): void { this.users.set(user.id, user); }
  findByEmail(email: string): User | undefined {
    return [...this.users.values()].find(u => u.email === email);
  }
}
```

**Best for:** Repositories, data stores, caches, queues. Anywhere you need realistic
behavior without infrastructure.

### Stubs — return predetermined responses

Stubs provide canned answers without any logic. Use them when you only need to
control what a dependency returns.

```python
class StubPriceService:
    def get_price(self, product_id):
        return 99.99
```

```typescript
const stubPriceService: PriceService = {
  getPrice: () => 99.99,
};
```

**Best for:** Simple read-only dependencies where the test needs a specific input value.

### Mocks — verify interactions

Mocks record calls and let you assert that interactions happened. Use sparingly —
they couple tests to implementation details.

```python
def test_sends_notification_on_order():
    notifier = Mock()
    service = OrderService(notifier=notifier)
    service.place_order(order)
    notifier.send.assert_called_once_with(order.customer_email)
```

```typescript
test('sends notification on order', () => {
  const notifier = { send: jest.fn() };
  const service = new OrderService(notifier);
  service.placeOrder(order);
  expect(notifier.send).toHaveBeenCalledWith(order.customerEmail);
});
```

**Best for:** Verifying side effects at system boundaries (email sent, event published,
API called). Avoid for internal method calls.

---

## The Mockery Anti-Pattern

Over-mocking makes tests brittle and meaningless. If every collaborator is mocked,
you're testing wiring, not behavior.

```python
# Everything is mocked — what is this actually testing?
def test_user_service():
    mock_repo = Mock()
    mock_validator = Mock()
    mock_hasher = Mock()
    mock_emailer = Mock()

    mock_validator.validate.return_value = True
    mock_hasher.hash.return_value = "hashed"
    mock_repo.save.return_value = User(id=1)

    service = UserService(mock_repo, mock_validator, mock_hasher, mock_emailer)
    service.create("test@test.com", "password")

    mock_validator.validate.assert_called_once()
    mock_hasher.hash.assert_called_once()
    mock_repo.save.assert_called_once()
```

This test breaks if you reorder internal calls, add a parameter, or change the
collaboration pattern — even if the behavior is identical.

**Fix — use real objects for internal logic, doubles only at boundaries:**
```python
def test_creates_user_with_hashed_password():
    repo = InMemoryUserRepository()
    service = UserService(repo)

    service.create("alice@test.com", "securepass123")

    user = repo.find_by_email("alice@test.com")
    assert user is not None
    assert user.password != "securepass123"  # Hashed, not plaintext
```

---

## Choosing the Right Double

| Situation | Use | Why |
|-----------|-----|-----|
| Database queries | Fake (in-memory repo) | Need realistic behavior |
| HTTP API calls | Stub or Fake | Control responses, avoid network |
| Email / SMS sending | Mock or Fake | Verify it was sent |
| System clock | Fake | Control time progression |
| File system | Fake or temp directory | Avoid real filesystem side effects |
| Internal business logic | **Real implementation** | Don't mock what you own |
| Pure functions | **Real implementation** | Fast and deterministic already |

The guiding question: **Would replacing this dependency with a double make the test
less realistic without good reason?** If yes, keep the real thing.
