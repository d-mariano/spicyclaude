#!/usr/bin/env bash
# Publish a design-breakdown directory to Jira via acli.
#
# Usage:
#   ./publish-breakdown-acli.sh <breakdown-dir> <project-key> [epic-key]
#
# Env (optional):
#   BATCH_LABEL  Label applied to every created ticket (default: <project-key>-v1, lowercased)
#   SITE         Atlassian site for jira-keys.md URLs (e.g. yoursite). Required for clickable links.
#   ASSIGNEE     Passed to --assignee on every create (default: unset).
#
# Behavior:
#   Pass 1 — create epic (or reuse [epic-key]), then create each child, append to jira-keys.md.
#   Pass 2 — read jira-keys.md, apply Blocks (from blocks_on) and Relates (from coordinates_with) links.
#
# Failure: stops loud on any acli error. jira-keys.md is the resume marker — re-running
# this script on a partial batch will recreate already-created tickets (no idempotency).
# To resume, comment out completed creates or trim the file list manually.

set -euo pipefail

BREAKDOWN_DIR="${1:?breakdown dir required}"
PROJECT_KEY="${2:?project key required}"
EPIC_KEY="${3:-}"
BATCH_LABEL="${BATCH_LABEL:-$(echo "$PROJECT_KEY" | tr '[:upper:]' '[:lower:]')-v1}"
SITE="${SITE:-}"

KEYMAP="$BREAKDOWN_DIR/jira-keys.md"

# --- Pre-flight ----------------------------------------------------------------

for cmd in acli yq jq awk sed; do
  command -v "$cmd" >/dev/null || { echo "ERROR: $cmd not on PATH" >&2; exit 1; }
done

acli jira project view --key "$PROJECT_KEY" >/dev/null || {
  echo "ERROR: acli auth or project lookup failed for $PROJECT_KEY" >&2
  exit 1
}

# --- Helpers -------------------------------------------------------------------

# Map lowercase frontmatter type → Jira issue type. Override here if your project
# uses custom names; the first failed create will tell you which.
map_type() {
  case "$1" in
    epic)  echo "Epic" ;;
    story) echo "Story" ;;
    task)  echo "Task" ;;
    bug)   echo "Bug" ;;
    spike) echo "Task" ;;  # most Jira projects lack Spike; title prefix carries intent
    *)     echo "ERROR: unknown type '$1'" >&2; exit 1 ;;
  esac
}

# Extract publishable body (strip frontmatter), summary (first H1), description (body minus H1).
# Writes /tmp/desc.md and echoes the summary.
extract_body() {
  local file="$1"
  sed '1{/^---$/!q;};1,/^---$/d' "$file" > /tmp/body.md
  awk 'found || !/^# /; /^# /{found=1; next}' /tmp/body.md > /tmp/desc.md
  awk '/^# /{print substr($0,3); exit}' /tmp/body.md
}

create_issue() {
  local file="$1" parent="$2"
  local type summary
  type="$(map_type "$(yq '.type' "$file")")"
  summary="$(extract_body "$file")"

  local args=(
    --project "$PROJECT_KEY"
    --type "$type"
    --summary "$summary"
    --description-file /tmp/desc.md
    --label "$BATCH_LABEL"
    --json
  )
  [ -n "$parent" ] && args+=(--parent "$parent")
  [ -n "${ASSIGNEE:-}" ] && args+=(--assignee "$ASSIGNEE")

  acli jira workitem create "${args[@]}" | jq -r '.key'
}

append_keymap_row() {
  local file="$1" key="$2"
  if [ -n "$SITE" ]; then
    printf '| `%s` | [%s](https://%s.atlassian.net/browse/%s) |\n' \
      "$(basename "$file")" "$key" "$SITE" "$key" >> "$KEYMAP"
  else
    printf '| `%s` | %s |\n' "$(basename "$file")" "$key" >> "$KEYMAP"
  fi
}

# --- Pass 1: create epic + children -------------------------------------------

# Build the file list: epic first (epic.md or epic-*.md), then NN-*.md sorted lexically.
mapfile -t EPIC_FILES < <(find "$BREAKDOWN_DIR" -maxdepth 1 -name 'epic*.md' | sort)
mapfile -t CHILD_FILES < <(find "$BREAKDOWN_DIR" -maxdepth 1 -regex '.*/[0-9]+[a-z]?-.*\.md' | sort)

[ "${#EPIC_FILES[@]}" -eq 1 ] || { echo "ERROR: expected exactly one epic-*.md, found ${#EPIC_FILES[@]}" >&2; exit 1; }
EPIC_FILE="${EPIC_FILES[0]}"

# Initialise keymap if absent.
if [ ! -f "$KEYMAP" ]; then
  cat > "$KEYMAP" <<EOF
# Jira keys for $PROJECT_KEY breakdown

| Markdown file | Jira key |
|---|---|
EOF
fi

if [ -z "$EPIC_KEY" ]; then
  echo "Creating epic from $(basename "$EPIC_FILE")..."
  EPIC_KEY="$(create_issue "$EPIC_FILE" "")"
  append_keymap_row "$EPIC_FILE" "$EPIC_KEY"
  echo "  → $EPIC_KEY"
else
  echo "Reusing existing epic $EPIC_KEY"
fi

for FILE in "${CHILD_FILES[@]}"; do
  echo "Creating $(basename "$FILE")..."
  KEY="$(create_issue "$FILE" "$EPIC_KEY")"
  append_keymap_row "$FILE" "$KEY"
  echo "  → $KEY"
done

# --- Pass 2: apply issue links ------------------------------------------------

# Build breakdown_id → KEY map from jira-keys.md, looking up each child file's frontmatter.
declare -A KEY_BY_ID
for FILE in "${CHILD_FILES[@]}"; do
  ID="$(yq '.breakdown_id' "$FILE")"
  KEY="$(grep -F "$(basename "$FILE")" "$KEYMAP" | grep -oE '[A-Z]+-[0-9]+' | head -1)"
  [ -n "$KEY" ] || { echo "ERROR: no key found for $FILE in $KEYMAP" >&2; exit 1; }
  KEY_BY_ID["$ID"]="$KEY"
done

LINK_COUNT_BLOCKS=0
LINK_COUNT_RELATES=0

for FILE in "${CHILD_FILES[@]}"; do
  ID="$(yq '.breakdown_id' "$FILE")"
  THIS_KEY="${KEY_BY_ID[$ID]}"

  # Blocks: each blocks_on entry → that ticket Blocks this one.
  # Confirm --from/--to flag shape against `acli jira workitem link --help` once per acli version.
  while IFS= read -r BLOCKER; do
    [ -z "$BLOCKER" ] || [ "$BLOCKER" = "null" ] && continue
    BLOCKER_KEY="${KEY_BY_ID[$BLOCKER]:-}"
    [ -n "$BLOCKER_KEY" ] || { echo "ERROR: blocks_on '$BLOCKER' in $FILE not in keymap" >&2; exit 1; }
    acli jira workitem link --type "Blocks" --from "$BLOCKER_KEY" --to "$THIS_KEY"
    LINK_COUNT_BLOCKS=$((LINK_COUNT_BLOCKS + 1))
  done < <(yq '.blocks_on[]' "$FILE" 2>/dev/null || true)

  # Relates: bidirectional, so dedup by (min, max) — only emit when processing the lower id.
  while IFS= read -r PEER; do
    [ -z "$PEER" ] || [ "$PEER" = "null" ] && continue
    [[ "$PEER" < "$ID" ]] && continue
    PEER_KEY="${KEY_BY_ID[$PEER]:-}"
    [ -n "$PEER_KEY" ] || { echo "ERROR: coordinates_with '$PEER' in $FILE not in keymap" >&2; exit 1; }
    acli jira workitem link --type "Relates" --from "$THIS_KEY" --to "$PEER_KEY"
    LINK_COUNT_RELATES=$((LINK_COUNT_RELATES + 1))
  done < <(yq '.coordinates_with[]' "$FILE" 2>/dev/null || true)
done

# --- Report -------------------------------------------------------------------

echo
echo "Done. Created $(( ${#CHILD_FILES[@]} + 1 )) issues in $PROJECT_KEY."
echo "Links applied: $LINK_COUNT_BLOCKS Blocks, $LINK_COUNT_RELATES Relates."
echo "Map persisted to $KEYMAP."
