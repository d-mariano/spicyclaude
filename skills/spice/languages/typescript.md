## TypeScript Conventions

> Load this skill for TypeScript/JavaScript implementation tasks.
> For TDD discipline, see the `test-driven-development` skill.

---

### Type System

#### Strict Mode (Required)

All projects must enable strict checking:

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "exactOptionalPropertyTypes": true,
    "noPropertyAccessFromIndexSignature": true
  }
}
```

#### Never Use `any`

```typescript
// ❌ BAD
function process(data: any) { ... }

// ✅ GOOD: Use unknown and narrow
function process(data: unknown): User {
  if (!isUser(data)) {
    throw new TypeError('Invalid user data');
  }
  return data;
}

// Type guard
function isUser(value: unknown): value is User {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    'email' in value
  );
}
```

#### Type Definitions

```typescript
// Interface for object shapes (preferred for objects)
interface User {
  readonly id: string;
  email: string;
  createdAt: Date;
}

// Type for unions, intersections, computed types
type Result<T, E = Error> = 
  | { ok: true; value: T } 
  | { ok: false; error: E };

// Utility types
type CreateUserDto = Omit<User, 'id' | 'createdAt'>;
type PartialUser = Partial<User>;
type ReadonlyUser = Readonly<User>;

// Discriminated unions
type Event = 
  | { type: 'USER_CREATED'; userId: string }
  | { type: 'USER_DELETED'; userId: string; reason: string };
```

---

### Code Style

#### Formatting (Automated)
- **Prettier** — Code formatting
- **ESLint** — Linting with `@typescript-eslint`

#### Naming
- `camelCase` — functions, variables, methods, properties
- `PascalCase` — classes, interfaces, types, enums, React components
- `SCREAMING_SNAKE_CASE` — constants
- `kebab-case` — file names (`user-service.ts`)

#### File Organization
```
src/
├── index.ts              # Public exports
├── types.ts              # Shared types (if needed)
├── {feature}/
│   ├── index.ts          # Feature exports
│   ├── {feature}.service.ts
│   ├── {feature}.types.ts
│   └── {feature}.test.ts
└── lib/
    └── {util}.ts
```

---

### Patterns

#### Immutability

```typescript
// Prefer const
const user = { name: 'Alice' } as const;

// Immutable updates
const updatedUser = { ...user, email: 'alice@test.com' };

// Readonly arrays
const roles: readonly string[] = ['admin', 'user'];

// Const assertions for literal types
const ROLES = ['admin', 'user', 'guest'] as const;
type Role = typeof ROLES[number]; // 'admin' | 'user' | 'guest'
```

#### Result Type for Error Handling

```typescript
type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E };

async function fetchUser(id: string): Promise<Result<User>> {
  try {
    const response = await api.get<User>(`/users/${id}`);
    return { success: true, data: response.data };
  } catch (error) {
    return { 
      success: false, 
      error: error instanceof Error ? error : new Error(String(error))
    };
  }
}

// Usage with narrowing
const result = await fetchUser('123');
if (!result.success) {
  console.error(result.error);
  return;
}
console.log(result.data.email); // TypeScript knows data exists
```

#### Null Handling

```typescript
// Optional chaining with nullish coalescing
const avatar = user?.profile?.avatar ?? '/default.png';

// Type guard for filtering
function isDefined<T>(value: T | null | undefined): value is T {
  return value != null;
}

const users = [user1, null, user2].filter(isDefined);
// users: User[] (not (User | null)[])

// Exhaustive checks
function handleEvent(event: Event): void {
  switch (event.type) {
    case 'USER_CREATED':
      console.log(`Created: ${event.userId}`);
      break;
    case 'USER_DELETED':
      console.log(`Deleted: ${event.userId}, reason: ${event.reason}`);
      break;
    default:
      // TypeScript error if we miss a case
      const _exhaustive: never = event;
      throw new Error(`Unhandled event: ${_exhaustive}`);
  }
}
```

#### Dependency Injection

```typescript
interface UserRepository {
  findById(id: string): Promise<User | undefined>;
  save(user: User): Promise<void>;
}

class UserService {
  constructor(private readonly repo: UserRepository) {}

  async activate(userId: string): Promise<User> {
    const user = await this.repo.findById(userId);
    if (!user) {
      throw new NotFoundError(`User ${userId} not found`);
    }
    const activated = { ...user, active: true };
    await this.repo.save(activated);
    return activated;
  }
}
```

#### Async Patterns

```typescript
// Parallel execution
const [user, posts] = await Promise.all([
  userService.getUser(id),
  postService.getUserPosts(id),
]);

// With error handling
const results = await Promise.allSettled([
  fetchUser(id1),
  fetchUser(id2),
]);

const users = results
  .filter((r): r is PromiseFulfilledResult<User> => r.status === 'fulfilled')
  .map(r => r.value);
```

---

### Testing

#### Framework
- **Vitest** or **Jest** — Test framework
- **@testing-library/react** — React testing
- **msw** — API mocking

#### Project Structure
```
src/
├── user/
│   ├── user.service.ts
│   └── user.service.test.ts    # Co-located
└── __tests__/                   # Integration tests
    └── api.test.ts
```

#### Test Pattern

```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest';

describe('UserService', () => {
  let service: UserService;
  let mockRepo: UserRepository;

  beforeEach(() => {
    mockRepo = {
      findById: vi.fn(),
      save: vi.fn(),
    };
    service = new UserService(mockRepo);
  });

  describe('activate', () => {
    it('returns activated user when user exists', async () => {
      vi.mocked(mockRepo.findById).mockResolvedValue({ 
        id: '1', 
        email: 'test@test.com',
        active: false 
      });

      const result = await service.activate('1');

      expect(result.active).toBe(true);
      expect(mockRepo.save).toHaveBeenCalledWith(
        expect.objectContaining({ active: true })
      );
    });

    it('throws NotFoundError when user does not exist', async () => {
      vi.mocked(mockRepo.findById).mockResolvedValue(undefined);

      await expect(service.activate('999'))
        .rejects
        .toThrow(NotFoundError);
    });
  });
});
```

#### React Testing

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

describe('LoginForm', () => {
  it('submits form with email and password', async () => {
    const onSubmit = vi.fn();
    render(<LoginForm onSubmit={onSubmit} />);

    await userEvent.type(screen.getByLabelText(/email/i), 'test@test.com');
    await userEvent.type(screen.getByLabelText(/password/i), 'password123');
    await userEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        email: 'test@test.com',
        password: 'password123',
      });
    });
  });
});
```

---

### Commands

```bash
# Testing (Vitest)
npm test                        # Run all
npm test -- --watch             # Watch mode
npm test -- --coverage          # With coverage
npm test -- --run               # Single run (CI)

# Testing (Jest)
npm test                        # Run all
npm test -- --watchAll          # Watch mode
npm test -- --coverage          # With coverage

# Formatting
npm run format                  # Prettier
npm run lint                    # ESLint
npm run lint -- --fix           # Auto-fix

# Type checking
npm run typecheck               # tsc --noEmit

# All validation
npm run lint && npm run typecheck && npm test
```

---

### Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Use `any` | Use `unknown` and narrow |
| `data as User` without check | Type guard first |
| Ignore Promise rejections | Handle or explicit `.catch()` |
| Mutate function params | Return new objects |
| Default exports | Named exports |
| Nested ternaries | Early returns or switch |
| `Boolean(value)` filtering | Proper type guards |
| Non-null assertion `!` | Proper null checks |
| Enum (prefer union types) | `type Status = 'active' \| 'inactive'` |

---

### Quick Reference

```typescript
// Modern TypeScript patterns
interface Props {
  readonly items: readonly Item[];
  onSelect?: (item: Item) => void;
}

// Generics with constraints
function first<T extends { id: string }>(items: T[]): T | undefined {
  return items[0];
}

// Mapped types
type Nullable<T> = { [K in keyof T]: T[K] | null };

// Template literal types
type EventName = `on${Capitalize<string>}`;

// Satisfies operator (TS 4.9+)
const config = {
  port: 3000,
  host: 'localhost',
} satisfies ServerConfig;
```
