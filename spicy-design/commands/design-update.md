---
argument-hint: "<path to design doc> <description of change>"
description: Revise an existing design document — targeted update, re-review affected sections
---

I need to update an existing technical design document:

$ARGUMENTS

Follow this process:

1. **Read the design document** at the specified path. Also read `task.md` in the same directory if it exists.

2. **Assess the scope of the change.** Classify it:
   - **Localized**: affects a single component, data flow, or contract. Update the affected sections only.
   - **Cross-cutting**: affects multiple components or changes an architectural decision. Update all affected sections and flag any ADRs (Phase 2) that need revision.
   - **Fundamental**: changes the architectural approach. This may need a new design — warn the user and ask whether to patch or restart.

3. **Present the impact assessment**: which sections of the design will change, which will stay the same, and whether any Phase 2 decisions are affected. Ask the user to confirm before editing.

4. **Make the targeted edits.** For each change:
   - Update the affected sections in place
   - Add a revision note at the top: `> **Revised**: {date} — {one-line summary of change}`
   - If contracts change, verify both sides of every affected component boundary still match
   - If the implementation phases change, update done conditions and dependencies

5. **Check downstream impact.** If a `plan.md` exists in the same directory:
   - List which plan tasks are affected by the design change
   - Tell the user: *"The plan at {path} has tasks affected by this change: {list}. Run `/spicy-workflow:planner {design path}` to regenerate, or manually update the affected tasks."*

6. **Re-run the reviewer** on the updated design using the Task tool, delegating to the `design-reviewer` agent. Include the original task description and the amendment description in the review prompt.

Save a backup of the pre-update design to `design.pre-update-{date}.md` before making any edits.
