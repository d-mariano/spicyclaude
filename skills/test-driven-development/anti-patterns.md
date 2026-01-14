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
