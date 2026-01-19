## Go Conventions

> Load this resource for Go implementation tasks.
> For TDD discipline, see the `test-driven-development` skill.

---

### Code Style

#### Formatting (Mandatory)
- **gofmt** — Required, no exceptions
- **goimports** — Import organization

```bash
gofmt -w .
goimports -w .
```

#### Naming
- `PascalCase` — Exported (public) identifiers
- `camelCase` — Unexported (private) identifiers
- **Short names** for locals: `i`, `n`, `err`, `ctx`
- **Descriptive** for exported: `UserRepository`, `ProcessOrder`
- Acronyms are all caps: `HTTPClient`, `userID`

```go
// Good: Short receiver names
func (s *Server) handleRequest(w http.ResponseWriter, r *http.Request) {}

// Good: Descriptive exports
type UserRepository interface {
    FindByID(ctx context.Context, id string) (*User, error)
}
```

#### Package Design
- Short, lowercase, no underscores
- One package = one purpose
- Avoid `util`, `common`, `helpers`

```
myapp/
├── cmd/server/main.go
├── internal/           # Private packages
│   ├── user/
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

// Sentinel errors
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
```

#### Interfaces

```go
// Accept interfaces, return structs
// Define interfaces where used, not implemented
// Keep small (1-3 methods)

package user

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
```

#### Context

```go
// First parameter for I/O functions
// Never store in structs
// Use for cancellation and timeouts

func (s *Service) ProcessOrder(ctx context.Context, orderID string) error {
    select {
    case <-ctx.Done():
        return ctx.Err()
    default:
    }
    
    user, err := s.users.GetUser(ctx, order.UserID)
    if err != nil {
        return fmt.Errorf("get order user: %w", err)
    }
    // ...
}
```

#### Concurrency

```go
// Use errgroup for parallel operations
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

func NewServer(addr string, opts ...ServerOption) *Server {
    s := &Server{
        addr:    addr,
        timeout: 30 * time.Second, // default
    }
    for _, opt := range opts {
        opt(s)
    }
    return s
}

// Usage
server := NewServer(":8080", WithTimeout(60*time.Second))
```

---

### Testing

#### Framework
- Standard `testing` package
- `testify/assert` acceptable
- `httptest` for HTTP
- `go-cmp` for comparisons

#### Structure
```
user/
├── user.go
├── user_test.go        # Co-located
└── testdata/           # Fixtures
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

---

### Commands

```bash
# Testing
go test ./...                    # Run all
go test -v ./...                 # Verbose
go test -race ./...              # Race detector
go test -cover ./...             # Coverage

# Formatting
gofmt -w .
goimports -w .
golangci-lint run                # Comprehensive lint

# Build
go build ./cmd/server
go run ./cmd/server
```

---

### Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Ignore errors `_, _ := f()` | Always handle |
| Naked returns | Named or explicit |
| Panic for expected errors | Return error |
| `init()` for complex setup | Explicit initialization |
| Stuttering `user.UserService` | `user.Service` |
| Large interfaces | Small, focused |
| Return interfaces | Return concrete types |
| Context in structs | Pass as first param |
| Goroutine leaks | Ensure exit path |
