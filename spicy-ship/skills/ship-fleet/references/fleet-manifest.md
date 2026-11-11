# Fleet manifest

One JSON file describes a fleet. Whoever plans the fleet writes the trunk and, for each story, the
first four fields; `ship-fleet` fills in the rest as stories run, in place.

```json
{
  "trunk": "main",
  "stories": [
    {"id": "S1", "story": "stories/s1-schema.md", "depends_on": [], "status": "pending"},
    {"id": "S2", "story": "stories/s2-api.md", "depends_on": ["S1"], "status": "pending"},
    {"id": "S3", "story": "stories/s3-docs.md", "depends_on": [], "status": "pending"}
  ]
}
```

| Field | Written by | Meaning |
|---|---|---|
| `id` | planner | unique within the fleet |
| `story` | planner | path of the story file, shaped like `ship-it`'s example story |
| `depends_on` | planner | ids of the stories whose code this one builds on |
| `status` | planner, then `ship-fleet` | `pending`, `running`, `needs_input`, `blocked` or `done` |
| `branch` | `ship-fleet` | the story's `ship/*` branch, set when it starts |
| `context` | `ship-fleet` | the story's context folder |
| `worktree` | `ship-fleet` | where its runner last worked; removed once the story is done |
| `pr` | `ship-fleet` | the pull request, once opened |
| `blocked_reason` | `ship-fleet` | why a blocked story stopped |

Here S1 and S3 start together on `main`, and S2 starts on S1's branch once S1 is done.

Two rules shape what a planner may write, and `fleet_plan.py` rejects a manifest that breaks them,
naming the story:

- List a story after every story it depends on.
- A story stacks on one branch. If it depends on several stories, one of them must depend on all
  the others, directly or through a chain.
