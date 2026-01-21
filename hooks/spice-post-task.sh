#!/bin/bash
# SPICE Post-Task Hook
# 
# This hook runs after each task completes in SPICE.
# It enables deterministic validation beyond what the subagent performs.
#
# Usage: Place in .claude/hooks/ and make executable
#        chmod +x .claude/hooks/spice-post-task.sh
#
# Arguments:
#   $1 - Context folder path (e.g., /context/001-feature/)
#   $2 - Task number completed (e.g., "2.1")
#   $3 - Test exit code (0 = pass, non-zero = fail)
#
# Exit codes:
#   0 - Validation passed
#   1 - Validation failed (stops workflow)

CONTEXT_FOLDER="$1"
TASK_NUMBER="$2"
TEST_EXIT_CODE="$3"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 SPICE Post-Task Hook"
echo "   Task: $TASK_NUMBER"
echo "   Context: $CONTEXT_FOLDER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Skip if tests already failed
if [ "$TEST_EXIT_CODE" != "0" ]; then
    echo "⏭️  Skipping hook (tests failed)"
    exit 1
fi

# Detect project type and run appropriate validation
if [ -f "pyproject.toml" ] || [ -f "requirements.txt" ] || [ -f "Pipfile" ]; then
    echo "🐍 Python project detected"
    
    # Detect package manager and run validation
    if [ -f "poetry.lock" ]; then
        echo "Using Poetry..."
        
        echo "Running mypy..."
        if ! poetry run mypy src/ 2>/dev/null; then
            echo "❌ mypy failed"
            exit 1
        fi
        echo "✅ mypy passed"
        
        echo "Running ruff..."
        if ! poetry run ruff check . 2>/dev/null; then
            echo "❌ ruff failed"
            exit 1
        fi
        echo "✅ ruff passed"
        
    elif [ -f "uv.lock" ]; then
        echo "Using uv..."
        
        echo "Running mypy..."
        if ! uv run mypy src/ 2>/dev/null; then
            echo "❌ mypy failed"
            exit 1
        fi
        echo "✅ mypy passed"
        
        echo "Running ruff..."
        if ! uv run ruff check . 2>/dev/null; then
            echo "❌ ruff failed"
            exit 1
        fi
        echo "✅ ruff passed"
        
    elif [ -f "Pipfile.lock" ]; then
        echo "Using Pipenv..."
        
        echo "Running mypy..."
        if ! pipenv run mypy src/ 2>/dev/null; then
            echo "❌ mypy failed"
            exit 1
        fi
        echo "✅ mypy passed"
        
        echo "Running ruff..."
        if ! pipenv run ruff check . 2>/dev/null; then
            echo "❌ ruff failed"
            exit 1
        fi
        echo "✅ ruff passed"
        
    else
        echo "Using pip/venv..."
        
        # Activate venv if it exists
        [ -f ".venv/bin/activate" ] && source .venv/bin/activate
        [ -f "venv/bin/activate" ] && source venv/bin/activate
        
        echo "Running mypy..."
        if ! mypy src/ 2>/dev/null; then
            echo "❌ mypy failed"
            exit 1
        fi
        echo "✅ mypy passed"
        
        echo "Running ruff..."
        if ! ruff check . 2>/dev/null; then
            echo "❌ ruff failed"
            exit 1
        fi
        echo "✅ ruff passed"
    fi

elif [ -f "package.json" ]; then
    echo "📦 Node.js project detected"
    
    # Type checking
    echo "Running TypeScript check..."
    if ! npm run typecheck 2>/dev/null; then
        echo "❌ TypeScript check failed"
        exit 1
    fi
    echo "✅ TypeScript check passed"
    
    # Linting
    echo "Running ESLint..."
    if ! npm run lint 2>/dev/null; then
        echo "❌ ESLint failed"
        exit 1
    fi
    echo "✅ ESLint passed"

elif [ -f "go.mod" ]; then
    echo "🔵 Go project detected"
    
    # Vet
    echo "Running go vet..."
    if ! go vet ./... 2>/dev/null; then
        echo "❌ go vet failed"
        exit 1
    fi
    echo "✅ go vet passed"
    
    # Linting
    echo "Running golangci-lint..."
    if command -v golangci-lint &> /dev/null; then
        if ! golangci-lint run 2>/dev/null; then
            echo "❌ golangci-lint failed"
            exit 1
        fi
        echo "✅ golangci-lint passed"
    fi

else
    echo "⚠️  Unknown project type, skipping language-specific checks"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ All post-task validations passed"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

exit 0
