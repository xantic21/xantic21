# GitHub-only branch retention: 14-day minimum · 24 November 2026

**Owner-authorized.** This is a repository-local GitHub Actions job, not an automation in ChatGPT, Claude, Cloudflare or HACC. The 14-day period is a **minimum**, and deletion is attempted only at the next weekly run.

**Schedule:** Sunday 04:43 UTC (`43 4 * * 0`). A manually triggered `workflow_dispatch` is **audit-only**; a pull request triggers read-only policy tests. Only the scheduled `main` cleanup job has `contents: write`.

**Conditions before deleting a branch:**
- A closed pull request from **this same repository** was merged to `main` at least 14 full days earlier.
- The **most recent PR using that branch** is the qualifying merge; no open PR uses the branch, and its current SHA exactly matches the merged PR head SHA.
- Only conservative `feat/`, `fix/`, `chore/`, `docs/` and `dependabot/` names; sensitive names with release, signing, approval, evidence, certification, audit, rollback, integration, backup, publishing, HACC, device, production, promotion, tags, records, or handover are denied.
- Default `main`, protected branches and branch tips matching any remote release tag or protected/retained ref SHA are excluded.
- Immediately before deletion, the job rechecks pull requests and the remote branch tip. It uses an atomic `--force-with-lease` Git push with the **expected exact SHA**, never an unguarded deletion or forced retry.
- No more than **five** verified deletions per repository per weekly execution. Missing or contradictory information prevents deletion.

## Repository-specific safeguards

The public profile README and icon assets are unchanged. The default main ruleset remains active; the workflow targets only obsolete fully merged low-risk documentation branches, never the profile content itself.

## Operational boundaries

The script and unit tests live at `tools/maintenance/`; the workflow lives at `.github/workflows/safe-branch-cleanup.yml`. If the GitHub Actions token cannot delete branches under GitHub's own repository rules, the workflow must fail closed; do not broaden secrets, change repository visibility or bypass rulesets. No tags, releases, application code, private data, deployed Workers or signing keys are modified. No GitHub Pro subscription or paid service is needed.

The three preexisting deployments in Coffee Lab, NFL Pulse and Henning Hub continue to use the same 14-day and SHA lease rules. HACC itself remains fully read-only.
