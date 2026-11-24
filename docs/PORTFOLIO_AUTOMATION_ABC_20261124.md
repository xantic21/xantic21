# Portfolio automation A/B/C — owner-approved, low-touch operation

This repository is one of seven in the **xantic21** portfolio. The goal is predictable maintenance without requiring ChatGPT, Claude, a paid GitHub plan, a desktop admin account, or new long-lived credentials.

## A — routine maintenance and incident tracking

- Weekly **Dependabot** proposals for supported ecosystems; group small dependency updates and cap open PR volume. Dependency upgrades never automatically publish a package, tag, APK, Worker or Connect IQ binary.
- Daily **Portfolio · CI Health and Release Readiness** GitHub Actions job checks completed main-branch CI, missing/discontinued scheduled tasks, and **two consecutive failures**. A failing workflow does not initiate an unbounded retry loop; persistent blockers receive one deduplicated GitHub Issue if Issues are enabled. Recovery closes only on positive evidence, not on missing API data.
- Manual Actions dispatch performs **read-only health audit + release readiness summary**, and no issue write.
- GitHub Actions and GitHub's notification preferences control notifications; no background ChatGPT session is required.

## B — resource efficiency

- Prefer dependency cache based on committed lockfiles, cancel only superseded pull-request runs, preserve main CI, use timeouts and explicit artifact retention.
- New guardrails are non-publishing. No emulator, Android, Cloudflare or Garmin production gate is bypassed solely to save minutes.
- Test receipts, signed release archives, security evidence and reproducible source manifests keep their established retention periods.

## C — automatic release preflight, **not** automatic publication

- Every Sunday and on owner-triggered manual dispatch, the GitHub workflow writes a **release readiness report to its run summary**, including live main SHA, outstanding PRs, recent tests, recent published tag and available artifact metadata.
- The report is **advisory**. It deliberately does not call production publishing or signing APIs and does not transform a test into an owner acceptance.
- Where it is safe, avoid repeated user confirmations for unmodified input: **a valid previous physical-device acceptance is reusable only for the exact same signed artifact SHA and unchanged installation/security conditions**. A newly built signed APK or Watchface requires real device acceptance unless a pre-existing, version-bound and explicitly owner-approved waiver is validated by the product's own gate.
- Routine static tests, synthetic demo generation, read-only queries and evidence collation **do not** need an additional manual owner GO. A single final owner release GO can replace multiple duplicative confirmations, but the final state change remains explicit.
- Never auto-merge an unreviewed production release, auto-approve a secret or access change, or claim unverified device/security tests.

### Product-specific interpretation

The public profile has only GitHub Actions dependencies. No product code, signing, deployment or release secrets are involved. Its status report is informational; it must not claim private repository coverage without explicit private-repository permissions.

## Fixed authority boundaries

Every workflow is repository-local, runs under its own `GITHUB_TOKEN` with job-level least privilege, and **does not write to other repositories**. HACC stays read-only to application repositories. Any optional dependency auto-merge or automated CI re-run needs a separate, verified allowlist and test plan; no blanket auto-merge is enabled. The CI and schedule health check is not a license to alter permissions, remove physical device gates, rotate keys, or publish releases.

**References:** `.github/workflows/portfolio-ops.yml`, `tools/portfolio/ops.py`, `tools/portfolio/test_ops.py`, `.github/workflows/safe-branch-cleanup.yml` and `.github/dependabot.yml` where present.
