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
