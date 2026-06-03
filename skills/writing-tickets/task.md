# Task

Technical or operational work with **no externally observable consumer surface**.

If the work creates or changes anything that a consumer (end user, API caller, downstream service, future engineer writing against the contract) can observe from outside the implementation, it's a **Story** — see [story.md](story.md). Tasks are reserved for work that's invisible from the outside:

- **Infrastructure provisioning** (Terraform resources, Cloud Logging alerts, IAM bindings, Secret Manager scaffolding) — the consumer is the platform itself, not a calling service.
- **Internal refactors with identical request/response shape** (worker-class flips, framework upgrades, dependency bumps) — observably bit-identical from the outside.
- **Shared internal helpers** with no public contract (a private SDK wrapper used only by sibling stories in the same service).
- **Build / CI / tooling changes** — Dockerfile entrypoint flips, codegen pipeline tweaks, lint config.
- **Pure deletions / cleanup** with no contract change.

Rule of thumb: if you can't write an AC in the form "When `<consumer>` does `<X>`, they observe `<Y>`", it's a Task. The Task's ACs are infrastructure-shaped: "the resource exists", "the entrypoint boots cleanly", "the dependency is on the supported version", "the dead code is gone".

## Template
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
