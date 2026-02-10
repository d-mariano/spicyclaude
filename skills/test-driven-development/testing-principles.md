# Testing Principles and Anti-Patterns

Every test must satisfy all five FIRST principles. Each principle below includes the
corresponding anti-pattern so you can recognize violations.

---

## Fast

Tests run in milliseconds. No real delays, no network calls, no disk I/O in unit tests.

**Anti-pattern — The Slow Poke:**
```python
# Waiting for real time
def test_session_expires():
    session = Session(timeout_seconds=300)
    time.sleep(301)
    assert session.is_expired()
```

**Fix — control time:**
```python
def test_session_expires():
    clock = FakeClock()
    session = Session(timeout_seconds=300, clock=clock)
    clock.advance(seconds=301)
    assert session.is_expired()
```

```typescript
// Same principle in TypeScript
test('session expires after timeout', () => {
  const clock = new FakeClock();
  const session = new Session({ timeoutMs: 300_000, clock });
  clock.advance(300_001);
  expect(session.isExpired()).toBe(true);
});
```

Inject clocks, HTTP clients, and file systems as dependencies so tests can substitute
fast fakes.

---

## Independent

Tests never depend on other tests or shared mutable state. Each test creates its own
state from scratch.

**Anti-pattern — Generous Leftovers:**
```python
# Shared mutable state leaks between tests
cart = Cart()

def test_add_item():
    cart.add(Item("Book", 10))
    assert cart.total == 10

def test_remove_item():  # Depends on test_add_item running first!
    cart.remove("Book")
    assert cart.total == 0
```

**Fix — isolate each test:**
```python
def test_add_item():
    cart = Cart()
    cart.add(Item("Book", 10))
    assert cart.total == 10

def test_remove_item():
    cart = Cart()
    cart.add(Item("Book", 10))
    cart.remove("Book")
    assert cart.total == 0
```

If a test creates files, database records, or temp state, clean up in teardown.
Prefer in-memory implementations for unit tests.

---

## Repeatable

Same result every time, everywhere. No environment dependencies, no randomness,
no reliance on machine-specific paths or configuration.

**Anti-pattern — The Local Hero:**
```python
# Breaks in CI
def test_reads_config():
    config = load_config()  # Reads from env vars that only exist locally
    assert config.database_url is not None

def test_reads_file():
    data = read_file("/Users/developer/project/data.json")
```

**Fix — inject all dependencies explicitly:**
```python
def test_reads_config():
    config = load_config(path="tests/fixtures/config.yaml")
    assert config.database_url == "postgres://test:5432/testdb"

def test_reads_file(tmp_path):
    test_file = tmp_path / "data.json"
    test_file.write_text('{"key": "value"}')
    data = read_file(str(test_file))
    assert data["key"] == "value"
```

**Anti-pattern — The Flaky Test:**
```python
# Non-deterministic
def test_generates_unique_id():
    id1 = generate_id()
    id2 = generate_id()
    assert id1 != id2  # Usually true, but not guaranteed
```

**Fix — control randomness:**
```python
def test_generates_unique_id():
    generator = IdGenerator(seed=12345)
    id1 = generator.next()
    id2 = generator.next()
    assert id1 != id2
    assert id1 == "expected-value-for-seed"
```

Rules: never use absolute paths, never assume environment variables exist, seed
all randomness.

---

## Self-Validating

Tests produce a binary pass/fail result. No manual inspection of logs or output.

**Anti-pattern — The Liar:**
```python
# Proves nothing
def test_calculates_tax():
    result = calculate_tax(100)
    assert True  # Always passes!

# Tests the mock, not the system
def test_sends_email():
    mock_sender = Mock()
    mock_sender.send.return_value = True
    assert mock_sender.send("test") == True
```

**Fix — assert meaningful outcomes:**
```python
def test_calculates_tax():
    assert calculate_tax(100) == 7.00

def test_sends_email():
    sender = FakeEmailSender()
    service = NotificationService(sender)
    service.notify("user@test.com", "Hello")
    assert sender.was_sent_to("user@test.com")
```

---

## Thorough

Cover happy paths, edge cases, boundaries, and error states.

```python
# Boundary coverage for pagination
def test_first_page_has_no_previous():
    assert paginate(items, page=1, per_page=10).has_previous == False

def test_last_page_has_no_next():
    items = list(range(25))
    assert paginate(items, page=3, per_page=10).has_next == False

def test_empty_collection():
    assert paginate([], page=1, per_page=10).items == []

def test_exact_page_boundary():
    items = list(range(20))
    assert paginate(items, page=2, per_page=10).has_next == False
```

---

## Additional Anti-Patterns

These don't map directly to a FIRST principle but are equally important to avoid.

### The Giant — tests that verify too many things

```python
# One test covering an entire workflow
def test_entire_checkout_flow():
    user = create_user()
    login(user)
    add_to_cart(product1)
    apply_coupon("SAVE10")
    place_order()
    verify_email_sent()
    verify_inventory_updated()
    verify_payment_charged()
```

Split into focused tests, each covering one behavior:
```python
def test_coupon_reduces_total():
    cart = Cart([Item(price=100)])
    cart.apply_coupon(Coupon("SAVE10", percent=10))
    assert cart.total == 90

def test_order_decrements_inventory():
    inventory = Inventory({"SKU1": 5})
    service = OrderService(inventory)
    service.place(Order(items=[{"sku": "SKU1", "qty": 2}]))
    assert inventory.count("SKU1") == 3
```

### The Inspector — tests coupled to internal implementation

```python
# Testing private internals
def test_cache_uses_lru_eviction():
    cache = Cache(max_size=2)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("c", 3)
    assert cache._internal_list[0].key == "b"  # Breaks on any refactor
```

Test observable behavior through the public interface:
```python
def test_cache_evicts_when_full():
    cache = Cache(max_size=2)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("c", 3)
    assert cache.get("c") == 3
    assert cache.size() == 2
```

If a private method needs direct testing, it probably belongs in its own class with
a public interface.
