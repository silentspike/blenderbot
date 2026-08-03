## Summary

<!-- What observable behaviour changes, and why is it required? -->

## Related issues

Refs #

## Scope boundary

**In scope**

-

**Explicitly unchanged**

<!-- Files and modules owned by other work in flight. -->

-

## Implementation audit

- [ ] Reread the complete live issue and the approved plan.
- [ ] Traced the change through its callers, persistence, recovery, consumers
      and observable effect — not just the edited function.
- [ ] Inspected the complete diff and the generated artifacts, not only test
      summaries.
- [ ] Recorded every untested, blocked or deferred surface below.

## Verification

### Focused iteration

<!-- Exact commands with their actual output. Include the matched/executed
     counts: a test filter that matches nothing also exits 0. -->

-

### Frozen-candidate gate

<!-- The required aggregate gate, run once after the implementation is final. -->

-

### Not run or still external

<!-- Name the surface and why it is not required, blocked or deferred.
     UNTESTED is a valid state; a green claim over an untested surface is not. -->

-

## Evidence and privacy

- [ ] Evidence is bound to the exact commit under test.
- [ ] No credential, token, account identity, provider raw data or unrelated
      local file is included.
- [ ] Temporary resources and live mutations were cleaned up.

## Landing checklist

- [ ] PR title follows Conventional Commits.
- [ ] Only owned files are staged; unrelated worktree changes remain untouched.
- [ ] Repository content is English-only.
- [ ] Promotion, tag or release has separate explicit authorization when applicable.
