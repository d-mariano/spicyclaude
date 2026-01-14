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
