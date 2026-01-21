## TypeScript Conventions

> Load this resource for TypeScript/JavaScript implementation tasks.
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
    "exactOptionalPropertyTypes": true
  }
}
```

#### Never Use `any`

```typescript
// BAD
function process(data: any) { ... }

// GOOD: Use unknown and narrow
function process(data: unknown): User {
  if (!isUser(data)) {
    throw new TypeError('Invalid user data');
  }
  return data;
}
```

#### Type Definitions

```typescript
// Interface for object shapes (preferred)
interface User {
  id: string;
  email: string;
  createdAt: Date;
}

// Type for unions and computed types
type Result<T> = 
  | { ok: true; value: T } 
  | { ok: false; error: Error };

// Utility types
type CreateUserDto = Omit<User, 'id' | 'createdAt'>;
type PartialUser = Partial<User>;
```

---

### Code Style

#### Formatting (Automated)
- **Prettier** — Code formatting
- **ESLint** — Linting with `@typescript-eslint`

#### Naming
- `camelCase` — functions, variables, methods
- `PascalCase` — classes, interfaces, types, enums, components
- `SCREAMING_SNAKE_CASE` — constants
- `kebab-case` — file names (`user-service.ts`)

#### File Organization
```
src/
├── index.ts              # Public exports
├── types.ts              # Shared types
├── {feature}/
│   ├── index.ts
│   ├── {feature}.ts
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
const user = { name: 'Alice' };

// Immutable updates
const updatedUser = { ...user, email: 'alice@test.com' };

// Readonly properties
interface Config {
  readonly apiUrl: string;
  readonly timeout: number;
}

// Const assertions
const ROLES = ['admin', 'user', 'guest'] as const;
type Role = typeof ROLES[number]; // 'admin' | 'user' | 'guest'
```

#### Error Handling

```typescript
// Result type for expected failures
type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E };

async function fetchUser(id: string): Promise<Result<User>> {
  try {
    const response = await api.get(`/users/${id}`);
    return { success: true, data: response.data };
  } catch (error) {
    return { 
      success: false, 
      error: new ServiceError('Fetch failed', { cause: error }) 
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
// Optional chaining
const avatar = user?.profile?.avatar ?? '/default.png';

// Type guard
function isDefined<T>(value: T | undefined): value is T {
  return value !== undefined;
}

const users = [user1, undefined, user2].filter(isDefined);
// users: User[] (not (User | undefined)[])
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

---

### Testing

#### Framework
- **Jest** or **Vitest** — Test framework
- **@testing-library/react** — React testing
- **vitest-mock-extended** or Jest mocks — Mocking

#### Structure
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
describe('UserService', () => {
  let service: UserService;
  let mockRepo: jest.Mocked<UserRepository>;

  beforeEach(() => {
    mockRepo = {
      findById: jest.fn(),
      save: jest.fn(),
    };
    service = new UserService(mockRepo);
  });

  describe('activate', () => {
    it('should return activated user when user exists', async () => {
      mockRepo.findById.mockResolvedValue({ id: '1', active: false });

      const result = await service.activate('1');

      expect(result.active).toBe(true);
    });

    it('should throw NotFoundError when user does not exist', async () => {
      mockRepo.findById.mockResolvedValue(undefined);

      await expect(service.activate('999')).rejects.toThrow(NotFoundError);
    });
  });
});
```

---

### Commands

```bash
# Testing
npm test                        # Run all
npm test -- --watch             # Watch mode
npm test -- --coverage          # With coverage

# Formatting
npm run format                  # Prettier
npm run lint                    # ESLint
npm run lint -- --fix           # Auto-fix

# Type checking
npm run typecheck               # tsc --noEmit
```

---

### Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Use `any` | Use `unknown` and narrow |
| `data as User` without check | Type guard first |
| Ignore Promise rejections | Handle or explicit `void` |
| Mutate function params | Return new objects |
| Default exports | Named exports |
| Nested ternaries | Early returns or switch |
| `Boolean(value)` filtering | Proper type guards |
