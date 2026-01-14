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
