## Go Conventions

> Load this skill for Go implementation tasks.
> For TDD discipline, see the `test-driven-development` skill.

---

### Code Style

#### Formatting (Mandatory)
- **gofmt** — Required, no exceptions
- **goimports** — Import organization
- **golangci-lint** — Comprehensive linting

```bash
gofmt -w .
goimports -w .
golangci-lint run
```

#### Naming
- `PascalCase` — Exported (public) identifiers
- `camelCase` — Unexported (private) identifiers
- **Short names** for locals: `i`, `n`, `err`, `ctx`, `r`, `w`
- **Descriptive** for exports: `UserRepository`, `ProcessOrder`
- Acronyms are all caps: `HTTPClient`, `userID`, `xmlParser`

```go
// Good: Short receiver names (1-2 letters)
func (s *Server) handleRequest(w http.ResponseWriter, r *http.Request) {}

// Good: Descriptive exports
type UserRepository interface {
    FindByID(ctx context.Context, id string) (*User, error)
}

// Good: Short local variables
for i, u := range users {
    if u.Active {
        result = append(result, u)
    }
}
```

#### Package Design
- Short, lowercase, no underscores
- One package = one purpose
- Avoid `util`, `common`, `helpers` — find better names

```
myapp/
├── cmd/
│   └── server/
│       └── main.go
├── internal/           # Private packages
│   ├── user/
│   │   ├── user.go
│   │   ├── user_test.go
│   │   └── repository.go
│   └── auth/
└── pkg/                # Public packages (if any)
    └── api/
```

---

### Patterns

#### Error Handling

```go
// Always check errors
result, err := doSomething()
if err != nil {
    return fmt.Errorf("do something: %w", err)
}

// Sentinel errors for expected conditions
var (
    ErrNotFound     = errors.New("not found")
    ErrUnauthorized = errors.New("unauthorized")
)

// Wrap with context
func (s *Service) GetUser(ctx context.Context, id string) (*User, error) {
    user, err := s.repo.FindByID(ctx, id)
    if err != nil {
        return nil, fmt.Errorf("get user %s: %w", id, err)
    }
    return user, nil
}

// Check wrapped errors
if errors.Is(err, ErrNotFound) {
    http.Error(w, "Not found", http.StatusNotFound)
    return
}

// Type assertion for error types
var validErr *ValidationError
if errors.As(err, &validErr) {
    http.Error(w, validErr.Message, http.StatusBadRequest)
    return
}
```

#### Interfaces

```go
// Accept interfaces, return structs
// Define interfaces where USED, not where implemented
// Keep small (1-3 methods)

package user

// Defined in the package that USES it
type Repository interface {
    FindByID(ctx context.Context, id string) (*User, error)
    Save(ctx context.Context, user *User) error
}

type Service struct {
    repo Repository
}

func NewService(repo Repository) *Service {
    return &Service{repo: repo}
}

func (s *Service) Activate(ctx context.Context, id string) (*User, error) {
    user, err := s.repo.FindByID(ctx, id)
    if err != nil {
        return nil, fmt.Errorf("find user: %w", err)
    }
    user.Active = true
    if err := s.repo.Save(ctx, user); err != nil {
        return nil, fmt.Errorf("save user: %w", err)
    }
    return user, nil
}
```

#### Context

```go
// First parameter for I/O functions
// Never store in structs
// Use for cancellation, timeouts, and request-scoped values

func (s *Service) ProcessOrder(ctx context.Context, orderID string) error {
    // Check cancellation at start of long operations
    select {
    case <-ctx.Done():
        return ctx.Err()
    default:
    }
    
    // Pass context through the call chain
    user, err := s.users.GetUser(ctx, order.UserID)
    if err != nil {
        return fmt.Errorf("get order user: %w", err)
    }
    
    // With timeout for external calls
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()
    
    return s.external.Notify(ctx, user.Email)
}
```

#### Concurrency

```go
// Use errgroup for parallel operations
import "golang.org/x/sync/errgroup"

func (s *Service) LoadDashboard(ctx context.Context, userID string) (*Dashboard, error) {
    g, ctx := errgroup.WithContext(ctx)
    
    var user *User
    var posts []*Post
    
    g.Go(func() error {
        var err error
        user, err = s.users.Get(ctx, userID)
        return err
    })
    
    g.Go(func() error {
        var err error
        posts, err = s.posts.ListByUser(ctx, userID)
        return err
    })
    
    if err := g.Wait(); err != nil {
        return nil, fmt.Errorf("load dashboard: %w", err)
    }
    
    return &Dashboard{User: user, Posts: posts}, nil
}

// Channel patterns
func generator(ctx context.Context, items []Item) <-chan Item {
    ch := make(chan Item)
    go func() {
        defer close(ch)
        for _, item := range items {
            select {
            case <-ctx.Done():
                return
            case ch <- item:
            }
        }
    }()
    return ch
}
```

#### Constructor Pattern

```go
// Functional options for complex construction
type ServerOption func(*Server)

func WithTimeout(d time.Duration) ServerOption {
    return func(s *Server) {
        s.timeout = d
    }
}

func WithLogger(l *slog.Logger) ServerOption {
    return func(s *Server) {
        s.logger = l
    }
}

func NewServer(addr string, opts ...ServerOption) *Server {
    s := &Server{
        addr:    addr,
        timeout: 30 * time.Second, // default
        logger:  slog.Default(),   // default
    }
    for _, opt := range opts {
        opt(s)
    }
    return s
}

// Usage
server := NewServer(":8080", 
    WithTimeout(60*time.Second),
    WithLogger(customLogger),
)
```

---

### Testing

#### Framework
- Standard `testing` package
- `testify/assert` acceptable for assertions
- `httptest` for HTTP testing
- `go-cmp` for complex comparisons

#### Project Structure
```
user/
├── user.go
├── user_test.go        # Co-located
├── service.go
├── service_test.go
└── testdata/           # Test fixtures
    └── users.json
```

#### Table-Driven Tests

```go
func TestService_GetUser(t *testing.T) {
    tests := []struct {
        name    string
        userID  string
        setup   func(*mockRepo)
        want    *User
        wantErr error
    }{
        {
            name:   "returns user when exists",
            userID: "123",
            setup: func(m *mockRepo) {
                m.users["123"] = &User{ID: "123", Name: "Alice"}
            },
            want: &User{ID: "123", Name: "Alice"},
        },
        {
            name:    "returns error when not found",
            userID:  "999",
            setup:   func(m *mockRepo) {},
            wantErr: ErrNotFound,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            t.Parallel()
            
            repo := newMockRepo()
            tt.setup(repo)
            svc := NewService(repo)

            got, err := svc.GetUser(context.Background(), tt.userID)

            if !errors.Is(err, tt.wantErr) {
                t.Errorf("error = %v, wantErr %v", err, tt.wantErr)
            }
            if diff := cmp.Diff(tt.want, got); diff != "" {
                t.Errorf("mismatch (-want +got):\n%s", diff)
            }
        })
    }
}
```

#### HTTP Handler Tests

```go
func TestHandler_CreateUser(t *testing.T) {
    svc := &mockService{
        createFunc: func(ctx context.Context, req CreateRequest) (*User, error) {
            return &User{ID: "1", Email: req.Email}, nil
        },
    }
    handler := NewHandler(svc)

    body := `{"email": "test@test.com", "name": "Test"}`
    req := httptest.NewRequest(http.MethodPost, "/users", strings.NewReader(body))
    req.Header.Set("Content-Type", "application/json")
    rec := httptest.NewRecorder()

    handler.ServeHTTP(rec, req)

    if rec.Code != http.StatusCreated {
        t.Errorf("status = %d, want %d", rec.Code, http.StatusCreated)
    }
    
    var resp User
    if err := json.NewDecoder(rec.Body).Decode(&resp); err != nil {
        t.Fatalf("decode response: %v", err)
    }
    if resp.Email != "test@test.com" {
        t.Errorf("email = %q, want %q", resp.Email, "test@test.com")
    }
}
```

#### Test Helpers

```go
// Helper functions reduce repetition
func mustParseTime(t *testing.T, s string) time.Time {
    t.Helper()
    parsed, err := time.Parse(time.RFC3339, s)
    if err != nil {
        t.Fatalf("parse time %q: %v", s, err)
    }
    return parsed
}

// Cleanup functions
func setupTestDB(t *testing.T) *sql.DB {
    t.Helper()
    db, err := sql.Open("sqlite3", ":memory:")
    if err != nil {
        t.Fatalf("open db: %v", err)
    }
    t.Cleanup(func() { db.Close() })
    return db
}
```

---

### Commands

```bash
# Testing
go test ./...                    # Run all
go test -v ./...                 # Verbose
go test -race ./...              # Race detector
go test -cover ./...             # Coverage
go test -coverprofile=cover.out ./... && go tool cover -html=cover.out

# Formatting
gofmt -w .
goimports -w .

# Linting
golangci-lint run
go vet ./...

# Build
go build ./cmd/server
go run ./cmd/server

# All validation
gofmt -l . && go vet ./... && golangci-lint run && go test -race ./...
```

---

### Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Ignore errors `_, _ := f()` | Always handle |
| Naked returns in long functions | Named or explicit |
| Panic for expected errors | Return error |
| `init()` for complex setup | Explicit initialization |
| Stuttering `user.UserService` | `user.Service` |
| Large interfaces (5+ methods) | Small, focused (1-3) |
| Return interfaces | Return concrete types |
| Context in structs | Pass as first param |
| Goroutine leaks | Ensure exit path |
| Premature channels | Start with sync code |

---

### Quick Reference

```go
// Modern Go patterns (1.21+)
package main

import (
    "cmp"
    "context"
    "log/slog"
    "slices"
)

// Structured logging
slog.Info("user created", 
    slog.String("user_id", user.ID),
    slog.Int("age", user.Age),
)

// Generic slices
users := slices.Clone(originalUsers)
slices.SortFunc(users, func(a, b *User) int {
    return cmp.Compare(a.Name, b.Name)
})

// Maps package
import "maps"
config := maps.Clone(defaultConfig)

// Clear builtin
clear(myMap)
clear(mySlice)
```
