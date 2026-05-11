#!/bin/bash

# Enhanced Claude Code Statusline
# Displays: time, user, directory, git status, context usage, and cost

input=$(cat)

MODEL_DISPLAY=$(echo "$input" | jq -r '.model.display_name // "Unknown"')
CURRENT_DIR=$(echo "$input" | jq -r '.workspace.current_dir // .cwd')
TOTAL_COST=$(echo "$input" | jq -r '.cost.total_cost_usd // 0')

CONTEXT_LIMIT=$(echo "$input" | jq -r '.context_window.context_window_size // 0')
CONTEXT_PCT=$(echo "$input" | jq -r '.context_window.used_percentage // empty' | cut -d. -f1)
CURRENT_CONTEXT=$(echo "$input" | jq -r '
    .context_window.current_usage as $u |
    if $u == null then empty
    else (($u.input_tokens // 0) + ($u.cache_read_input_tokens // 0) + ($u.cache_creation_input_tokens // 0))
    end')

TIME_STR=$(date '+%H:%M:%S')
USER_STR=$(whoami)
DIR_STR=$(basename "$CURRENT_DIR")

GIT_INFO=""
if git -C "$CURRENT_DIR" rev-parse --git-dir > /dev/null 2>&1; then
    BRANCH=$(git -C "$CURRENT_DIR" branch --show-current 2>/dev/null)
    if [ -n "$BRANCH" ]; then
        if ! git -C "$CURRENT_DIR" diff --quiet 2>/dev/null || \
           ! git -C "$CURRENT_DIR" diff --cached --quiet 2>/dev/null; then
            GIT_INFO=$(printf " on \033[33m%s*\033[0m" "$BRANCH")
        else
            GIT_INFO=$(printf " on \033[32m%s\033[0m" "$BRANCH")
        fi
    fi
fi

CONTEXT_INFO=""
if [ -n "$CURRENT_CONTEXT" ] && [ -n "$CONTEXT_PCT" ] && [ "$CONTEXT_LIMIT" -gt 0 ] 2>/dev/null; then
    if [ "$CONTEXT_PCT" -ge 80 ]; then
        CONTEXT_COLOR="\033[31m"
    elif [ "$CONTEXT_PCT" -ge 50 ]; then
        CONTEXT_COLOR="\033[33m"
    elif [ "$CONTEXT_PCT" -ge 16 ]; then
        CONTEXT_COLOR="\033[93m"
    else
        CONTEXT_COLOR="\033[32m"
    fi

    if [ "$CURRENT_CONTEXT" -ge 1000 ]; then
        TOKEN_DISPLAY=$(echo "scale=1; $CURRENT_CONTEXT / 1000" | bc 2>/dev/null)
        CONTEXT_LIMIT_DISPLAY=$(echo "scale=0; $CONTEXT_LIMIT / 1000" | bc 2>/dev/null)
        CONTEXT_INFO=$(printf " | %b%sK/%sK (%s%%)\\033[0m" "$CONTEXT_COLOR" "$TOKEN_DISPLAY" "$CONTEXT_LIMIT_DISPLAY" "$CONTEXT_PCT")
    else
        CONTEXT_INFO=$(printf " | %b%s/%s (%s%%)\\033[0m" "$CONTEXT_COLOR" "$CURRENT_CONTEXT" "$CONTEXT_LIMIT" "$CONTEXT_PCT")
    fi
fi

COST_INFO=""
if [ "$(echo "$TOTAL_COST > 0" | bc)" -eq 1 ]; then
    COST_INFO=$(printf " | \$%.4f" "$TOTAL_COST")
fi

printf "\033[2m%s %s\033[0m in \033[36m%s\033[0m%s | \033[35m%s\033[0m%s%s" \
    "$TIME_STR" \
    "$USER_STR" \
    "$DIR_STR" \
    "$GIT_INFO" \
    "$MODEL_DISPLAY" \
    "$CONTEXT_INFO" \
    "$COST_INFO"
