---
name: test-driven-development
description: ALWAYS use this skill when writing code. TDD is mandatory for all new code, features, bug fixes, and refactoring. Only exceptions are pure configuration files (JSON, YAML, env files) and documentation. Triggers on ANY code-related request. Enforces RED-GREEN-REFACTOR cycle without exception.
---

# Test-Driven Development (TDD) — Mandatory Protocol

**TDD is not optional.** Every line of functional code must be driven by a test. This is non-negotiable.

## When to Use TDD

### ALWAYS Use TDD For:
- New features or functionality
- Bug fixes (write a failing test that reproduces the bug first)
- Refactoring existing code
- API endpoints
- Business logic
- Data transformations
- Utility functions
- Class methods
- Database operations
- Integration points

### The ONLY Exceptions:
- Pure configuration files (JSON, YAML, .env, tsconfig, etc.)
- Documentation and comments
- Type definitions with no runtime behavior
- Import/export statements only

**Do not rationalize skipping TDD.** "It's too simple" is not an excuse. "I'll add tests later" is not acceptable. "This is just a quick fix" still requires a test first.

---

## The TDD Cycle: RED → GREEN → REFACTOR

Execute this cycle for **every piece of functionality**. Do not skip steps.

### 🔴 RED Phase: Write a Failing Test

Write ONE test that describes the desired behavior. Run it. It MUST fail.

```python
# Example: Building a password validator
def test_password_rejects_less_than_8_characters():
    validator = PasswordValidator()
    assert validator.is_valid("short") == False
```

**RED Phase Rules:**
- Write exactly ONE test at a time
- Test MUST fail for the right reason (missing functionality, not syntax errors)
- Run the test to confirm failure before proceeding
- Test name describes expected behavior
- Keep tests focused on ONE behavior

**Gate Check:** If the test passes, STOP. Either the functionality already exists or your test is wrong.

### 🟢 GREEN Phase: Make It Pass

Write the MINIMUM code to make the test pass. Nothing more.

```python
class PasswordValidator:
    def is_valid(self, password: str) -> bool:
        return len(password) >= 8
```

**GREEN Phase Rules:**
- Write ONLY enough code to pass the current failing test
- Hardcoding is acceptable if it passes (refactor later)
- Do NOT add features not required by a test
- Do NOT optimize
- Run all tests to confirm they pass

**Gate Check:** All tests must be green before proceeding.

### 🔵 REFACTOR Phase: Improve the Code

Clean up while keeping all tests green. Improve BOTH production and test code.

```python
class PasswordValidator:
    MIN_LENGTH = 8
    
    def is_valid(self, password: str) -> bool:
        return self._meets_length_requirement(password)
    
    def _meets_length_requirement(self, password: str) -> bool:
        return len(password) >= self.MIN_LENGTH
```

**REFACTOR Phase Rules:**
- All tests MUST remain passing throughout
- Remove duplication
- Improve naming and clarity
- Run tests after EVERY small change
- If tests fail, revert immediately

---

## The FIRST Principles of Good Tests

Every test you write must satisfy ALL five principles:

### **F — Fast**
Tests execute in milliseconds. No `sleep()`, no waiting.
```python
# BAD: Real delays
def test_session_expires():
    session = Session(timeout_seconds=300)
    time.sleep(301)  # 5 minutes!
    assert session.is_expired()

# GOOD: Control time
def test_session_expires():
    clock = FakeClock()
    session = Session(timeout_seconds=300, clock=clock)
    clock.advance(seconds=301)
    assert session.is_expired()
```

### **I — Independent**
Tests never depend on other tests or shared mutable state.
```python
# BAD: Shared state
cart = Cart()  # Shared across tests!

def test_add_item():
    cart.add(Item("Book", 10))
    assert cart.total == 10

def test_remove_item():  # Depends on test_add_item!
    cart.remove("Book")
    assert cart.total == 0

# GOOD: Each test isolated
def test_add_item_to_cart():
    cart = Cart()
    cart.add(Item("Book", 10))
    assert cart.total == 10

def test_remove_item_from_cart():
    cart = Cart()
    cart.add(Item("Book", 10))
    cart.remove("Book")
    assert cart.total == 0
```

### **R — Repeatable**
Same result every time, everywhere. No environment dependencies.
```python
# BAD: Non-deterministic
def test_generates_unique_id():
    id1 = generate_id()
    id2 = generate_id()
    assert id1 != id2  # Usually true, not guaranteed

# GOOD: Deterministic
def test_generates_unique_id():
    generator = IdGenerator(seed=12345)
    id1 = generator.next()
    id2 = generator.next()
    assert id1 != id2
    assert id1 == "expected-value-for-seed"
```

### **S — Self-Validating**
Binary pass/fail. No manual log inspection.
```python
# BAD: Requires manual inspection
def test_calculates_tax():
    result = calculate_tax(100)
    print(result)  # "Check if this looks right"

# GOOD: Explicit assertion
def test_calculates_tax():
    assert calculate_tax(100) == 7.00
```

### **T — Thorough**
Cover happy paths, edge cases, boundaries, and error states.
```python
def test_pagination_first_page():
    assert paginate(items, page=1, per_page=10).has_previous == False

def test_pagination_last_page():
    items = list(range(25))
    assert paginate(items, page=3, per_page=10).has_next == False

def test_pagination_empty_list():
    assert paginate([], page=1, per_page=10).items == []

def test_pagination_exact_multiple():
    items = list(range(20))
    assert paginate(items, page=2, per_page=10).has_next == False
```

---

## Test Structure: Arrange-Act-Assert (AAA)

Every test follows this structure. No exceptions.

```python
def test_user_receives_welcome_email_after_registration():
    # ARRANGE: Set up preconditions
    email_service = FakeEmailService()
    user_service = UserService(email_service)
    
    # ACT: Execute ONE behavior
    user_service.register("alice@example.com")
    
    # ASSERT: Verify expected outcome
    assert email_service.sent_to("alice@example.com")
    assert "Welcome" in email_service.last_subject()
```

**AAA Rules:**
- **Arrange**: Set up SUT and dependencies. Keep minimal.
- **Act**: Execute exactly ONE method or trigger ONE event.
- **Assert**: Verify return value, state, or side effect.

If you're acting on multiple things, you're testing too much. Split the test.

---

## Test Naming

Names describe BEHAVIOR, not implementation:

```python
# GOOD: Describes behavior
def test_expired_subscription_denies_access():
def test_admin_can_delete_any_post():
def test_empty_cart_shows_zero_total():

# BAD: Describes implementation
def test_check_expiry_returns_false():
def test_delete_method_called():
def test_get_total_function():
```

---

## Test Doubles: When to Use What

### Fakes
Working implementations with shortcuts (in-memory database):
```python
class FakePaymentGateway:
    def __init__(self):
        self.charges = []
    
    def charge(self, amount, card):
        self.charges.append((amount, card))
        return {"status": "success", "id": "fake-123"}
```

### Stubs
Return predetermined responses:
```python
class StubPriceService:
    def get_price(self, product_id):
        return 99.99
```

### Mocks
Verify interactions occurred:
```python
def test_sends_notification_on_order():
    notifier = Mock()
    order_service = OrderService(notifier)
    order_service.place_order(order)
    notifier.send.assert_called_once_with(order.customer_email)
```

**Golden Rule:** Only mock volatile external dependencies (HTTP, DB, FileSystem). Never mock the unit under test.

---

## Anti-Patterns: The Seven Deadly Sins of Testing

### 🎭 The Liar
**Tests that pass but verify nothing.**

```python
# ANTI-PATTERN: Always passes
def test_calculates_tax():
    result = calculate_tax(100)
    assert True  # Proves nothing!

# ANTI-PATTERN: Testing the mock
def test_sends_email():
    mock_sender = Mock()
    mock_sender.send.return_value = True
    assert mock_sender.send("test") == True  # Tests the mock!

# CORRECT
def test_calculates_tax():
    assert calculate_tax(100) == 7.00

def test_sends_email():
    sender = FakeEmailSender()
    service = NotificationService(sender)
    service.notify("user@test.com", "Hello")
    assert sender.was_sent_to("user@test.com")
```

---

### 🦣 The Giant
**Tests that are too large and verify too many things.**

```python
# ANTI-PATTERN: Massive test
def test_entire_checkout_flow():
    user = create_user()
    login(user)
    add_to_cart(product1)
    add_to_cart(product2)
    apply_coupon("SAVE10")
    set_shipping_address(address)
    set_payment_method(card)
    place_order()
    verify_email_sent()
    verify_inventory_updated()
    verify_payment_charged()
    # 50 more lines...

# CORRECT: Focused tests
def test_coupon_reduces_total():
    cart = Cart([Item(price=100)])
    cart.apply_coupon(Coupon("SAVE10", percent=10))
    assert cart.total == 90

def test_order_decrements_inventory():
    inventory = Inventory({"SKU1": 5})
    order_service = OrderService(inventory)
    order_service.place(Order(items=[{"sku": "SKU1", "qty": 2}]))
    assert inventory.count("SKU1") == 3
```

---

### 🃏 The Mockery
**Over-mocking that tests implementation, not behavior.**

```python
# ANTI-PATTERN: Testing wiring, not behavior
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
    # Tests the wiring, not the behavior!

# CORRECT: Real objects where practical
def test_user_service_creates_user():
    repo = InMemoryUserRepository()
    service = UserService(repo)
    
    service.create("alice@test.com", "securepass123")
    
    user = repo.find_by_email("alice@test.com")
    assert user is not None
    assert user.password != "securepass123"  # Should be hashed
```

**Rule:** Only mock external boundaries. Never mock internal logic.

---

### 🔍 The Inspector
**Tests that break when implementation changes, even if behavior is correct.**

```python
# ANTI-PATTERN: Testing internal implementation
def test_cache_uses_lru_eviction():
    cache = Cache(max_size=2)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.get("a")
    cache.set("c", 3)
    
    # Inspecting internal structure!
    assert cache._internal_list[0].key == "b"
    assert cache._eviction_count == 1

# CORRECT: Test observable behavior
def test_cache_evicts_when_full():
    cache = Cache(max_size=2)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("c", 3)
    
    assert cache.get("c") == 3  # New item exists
    assert cache.size() == 2    # Size maintained
```

**Rule:** Test the PUBLIC interface only. If a private method needs testing, extract it to a new class.

---

### 🐌 The Slow Poke
**Tests that are unnecessarily slow.**

```python
# ANTI-PATTERN: Real delays
def test_session_expires():
    session = Session(timeout_seconds=300)
    time.sleep(301)  # 5 minutes!
    assert session.is_expired()

# ANTI-PATTERN: Real network calls
def test_api_returns_data():
    response = requests.get("https://api.example.com/data")
    assert response.status_code == 200

# CORRECT: Control time and mock network
def test_session_expires():
    clock = FakeClock()
    session = Session(timeout_seconds=300, clock=clock)
    clock.advance(seconds=301)
    assert session.is_expired()

def test_api_returns_data():
    fake_client = FakeHttpClient(responses={"/data": {"status": 200}})
    service = DataService(fake_client)
    assert service.fetch_data().status == 200
```

---

### 🎲 The Flaky Test
**Tests that sometimes pass and sometimes fail.**

```python
# ANTI-PATTERN: Non-deterministic
def test_generates_unique_id():
    id1 = generate_id()
    id2 = generate_id()
    assert id1 != id2  # Usually true, not guaranteed

def test_timeout_handling():
    result = fetch_with_timeout(url, timeout=0.001)
    # Network timing is unpredictable

# CORRECT: Control randomness and timing
def test_generates_unique_id():
    generator = IdGenerator(seed=12345)
    id1 = generator.next()
    id2 = generator.next()
    assert id1 != id2
    assert id1 == "expected-value-for-seed"

def test_timeout_handling():
    slow_server = FakeServer(delay_seconds=10)
    result = fetch_with_timeout(slow_server.url, timeout=1)
    assert result.is_timeout_error
```

---

### 🏠 The Local Hero
**Tests that pass locally but fail in CI/CD.**

```python
# ANTI-PATTERN: Environment dependency
def test_reads_config():
    config = load_config()  # Reads from disk or env vars
    assert config.database_url is not None

def test_reads_file():
    data = read_file("/Users/developer/project/data.json")
    assert data is not None

# CORRECT: Explicit dependencies
def test_reads_config():
    config = load_config(path="/test/fixtures/config.yaml")
    assert config.database_url == "postgres://test:5432/testdb"

def test_reads_file():
    with tempfile.NamedTemporaryFile() as f:
        f.write(b'{"key": "value"}')
        f.flush()
        data = read_file(f.name)
        assert data["key"] == "value"
```

**Rules:**
- Never use absolute paths
- Never assume environment variables exist
- Inject all configuration

---

### 🗑️ Generous Leftovers
**Tests that pollute state for other tests.**

```python
# ANTI-PATTERN: No cleanup
def test_creates_temp_file():
    with open("/tmp/test_data.txt", "w") as f:
        f.write("test")
    result = process_file("/tmp/test_data.txt")
    assert result == "processed"
    # File left behind!

def test_inserts_user():
    db.insert(User(email="test@test.com"))
    assert db.count() == 1
    # Record left in database!

# CORRECT: Always clean up
def test_creates_temp_file():
    try:
        with open("/tmp/test_data.txt", "w") as f:
            f.write("test")
        result = process_file("/tmp/test_data.txt")
        assert result == "processed"
    finally:
        os.remove("/tmp/test_data.txt")

def test_inserts_user():
    db.begin_transaction()
    try:
        db.insert(User(email="test@test.com"))
        assert db.count() == 1
    finally:
        db.rollback()
```

**Rules:**
- Every test is idempotent
- Use `afterEach` / `finally` / teardown
- Prefer in-memory databases for unit tests

---

## Quick Reference: Good vs Bad Tests

| Aspect | ✅ Good Test | ❌ Bad Test |
|--------|-------------|-------------|
| **Speed** | Runs in milliseconds | Uses sleep(), real network |
| **Independence** | Creates own state | Depends on other tests |
| **Determinism** | Same result every run | Random failures |
| **Validation** | Clear assertions | console.log inspection |
| **Scope** | One behavior | Entire workflow |
| **Coupling** | Tests public interface | Tests private implementation |
| **Mocking** | Only external boundaries | Everything mocked |
| **Naming** | Describes behavior | Describes implementation |
| **Cleanup** | Leaves no trace | Pollutes environment |

---

## TDD Workflow Summary

1. **THINK**: What behavior do I need? What's the simplest test case?
2. **RED**: Write ONE failing test that describes the behavior
3. **GREEN**: Write MINIMAL code to pass the test
4. **REFACTOR**: Clean up while tests stay green
5. **REPEAT**: Next behavior, next test

**When stuck:** Take smaller steps. Even a hardcoded return value that passes is progress. The next test will force generalization.

**Remember:** TDD is a design discipline, not just verification. The test drives the design. If you're writing implementation first, you're not doing TDD.
