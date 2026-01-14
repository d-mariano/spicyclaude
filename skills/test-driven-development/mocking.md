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
