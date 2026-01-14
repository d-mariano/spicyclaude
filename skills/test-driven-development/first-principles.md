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
