---
name: create-jira
description: Creates and updates Jira issues of multiple types. Use when creating or updating Jira tickets, tracking work in Jira, or when the user asks to create a Jira ticket.
---

# Definitions
- **Acceptance Criteria**: observable behaviour or deliverables. Testable from the outside.
- **Engineering Notes**: how-to. Libraries, patterns, code pointers, citations.
- **Issue Links** (blocks / is blocked by / relates to) and **Epic parent** are Jira fields, not body content. Set them via `additional_fields` on `createJiraIssue`; if create drops them, follow up with `editJiraIssue`.
- Never create subtasks. Use issue links instead.

# Steps
- ALWAYS use the issue template for the correct issue
- If there are any gaps in the details, push back with clarifying questions in order to fulfill the template
- Create one or more issues to capture the details
- Always attach created Stories, Spikes, Tasks, or Bugs to an Epic unless instructed otherwise
- If you are unsure which Epic to attach to, ask which Epic to attach to
- Always include reference and resource links in Engineering Notes and even Summary when applicable
- When referencing code or files, link to a canonical repo URL (e.g. a GitHub permalink at the current commit, derived from `git remote` and `git rev-parse HEAD`) rather than a bare path — tickets must stand on their own
- Do not write large chunks of tests or novels
- Communicate effectively and keep it to the point
- Conduct any web searches that you may need on frameworks in use, unless the usage examples in code are telling enough
- Always refer to usage examples and best practices when found
- Research if third-party packages in use already provide required types and explicitly call this out
- If alternative approaches are identified and you have identified a preference, only mention your preference
- Favour simplicity and elegance
- Always cite your sources

# Issue Types
You may create the following types of issues as you see fit:
- **Epic**: Should really only be used on request, meant for multi-sprint features that are typically born from a PRD
- **Spike**: Use to capture research or PoC work that may potentially produce more issues
- **Story**: Use to capture features and user stories of an epic
- **Task**: Use to capture technical or operational tasks of an epic
- **Bug**: Use to capture bugs

# Issue Templates

## Epic
```markdown
# Summary
We are doing this feature so that we can support and enable the following.

# Motivation
Background on why we are doing this feature in the first place.

# Resources
- PRD
- Designs
- Confluence
```

## Spike
```markdown
# Summary
Describe the research or PoC to be done in order to fulfill the spike. Include reasoning as well.

# Acceptance Criteria
- Recommendation written in the ticket: graduate, pivot, or abandon
- Findings and supporting evidence captured in the ticket

# Engineering Notes
- A good place to start in code
- A good place to start in documentation (internal/external/etc)
```

## Story
```markdown
# Summary
Summary of the story and purpose.

# Acceptance Criteria
- [ ] As a user doing this, I need this, so that I can do that
- [ ] As a user doing this, I should see this
- [ ] As a user doing that, I should not see that

# Engineering Notes
- [Figma Design](https://link.to/design)
- [API Implementation](https://link.to/api/implementation)
- Utility is here
- Existing pattern in place here, reuse existing pattern
- Docs here
```

## Task
```markdown
# Summary
Do this thing so we have that done

# Acceptance Criteria
- The thing is done and verifiable from the outside
- The new capability is available where expected

# Engineering Notes
- Infra code here
- Existing module in place here
```

## Bug
```markdown
# Summary
Loading x results never loads when using filter y.

# Steps to Reproduce
1. Access portal [here](https://link.to.portal)
2. Click on thing
3. Filter for y

# Results
x results never loads, spinner keeps spinning, no feedback

# Expected Results
x results loads successfully, user is notified if there is an error

# Engineering Notes
- Error logs here
- Implementation of API here
- UI triggers filter here and loads results here
```

# Output
- Output any issues created
