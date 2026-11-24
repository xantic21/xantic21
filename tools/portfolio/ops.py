#!/usr/bin/env python3
"""Read-only portfolio health/release intelligence; optionally dedupe CI blocker issues."""
import argparse
from datetime import datetime, timedelta, timezone
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

POLICY = {
    "coffee-lab": {"qa": ["quality.yml"], "schedules": {"safe-branch-cleanup.yml": 7, "hacc-maintenance.yml": 7}},
    "nfl-pulse": {"qa": ["quality.yml"], "schedules": {"safe-branch-cleanup.yml": 7, "nfl-data-vintages.yml": 1}},
    "henning-hub": {"qa": ["hacc-quality.yml"], "schedules": {"safe-branch-cleanup.yml": 7, "hacc-maintenance.yml": 7}},
    "stride": {"qa": ["stride-ci.yml"], "schedules": {"safe-branch-cleanup.yml": 7}},
    "garmin-chatgpt-cockpit": {"qa": ["offline-tests.yml"], "schedules": {"safe-branch-cleanup.yml": 7, "daily-integrity.yml": 1, "garmin-readonly-sync.yml": 1, "garmin-incremental-backfill.yml": 1}},
    "hevy2garmin": {"qa": ["ci.yml"], "schedules": {"safe-branch-cleanup.yml": 7}},
    "xantic21": {"qa": [], "schedules": {"safe-branch-cleanup.yml": 7}},
}
FIRST_RUN_GRACE_END = datetime(2026, 12, 8, tzinfo=timezone.utc)
BLOCKER_PREFIX = "[Portfolio CI]"
REQUEST_TIMEOUT = 20


def parse_date(raw):
    if not isinstance(raw, str):
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def failing_twice(runs, now):
    completed = [run for run in runs if run.get("status") == "completed"
                 and run.get("conclusion") in ("success", "failure", "timed_out", "cancelled")]
    if len(completed) < 2:
        return False
    when = parse_date(completed[0].get("updated_at"))
    return bool(when and now - when < timedelta(days=14) and
                all(run.get("conclusion") in ("failure", "timed_out") for run in completed[:2]))


def success_twice(runs):
    completed = [run for run in runs if run.get("status") == "completed"]
    return len(completed) >= 2 and all(run.get("conclusion") == "success" for run in completed[:2])


def schedule_problem(status, runs, days, now):
    if status != "active":
        return "inactive or disabled workflow"
    scheduled = [run for run in runs if run.get("event") == "schedule"]
    if not scheduled:
        return "no scheduled execution observed" if now >= FIRST_RUN_GRACE_END else None
    latest = scheduled[0]
    when = parse_date(latest.get("created_at"))
    if when is None:
        return None
    if now - when > timedelta(days=days + 3):
        return "scheduled execution overdue"
    if failing_twice(scheduled, now):
        return "two consecutive scheduled failures"
    return None


def api(repository, path, method="GET", payload=None):
    token = os.environ.get("GH_TOKEN")
    if not token:
        raise RuntimeError("Missing job-scoped GITHUB_TOKEN")
    request = urllib.request.Request(
        "https://api.github.com/repos/" + repository + "/" + path.lstrip("/"),
        method=method,
        headers={"Authorization": "Bearer " + token,
                 "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28",
                 "User-Agent": "xantic21-portfolio-ops"},
        data=json.dumps(payload).encode("utf-8") if payload is not None else None)
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
        return json.load(response)


def checks(repository, policy, now):
    found = {}
    rows = []
    for name in policy["qa"]:
        try:
            data = api(repository, "actions/workflows/" + name + "/runs?branch=main&per_page=15")
            runs = data.get("workflow_runs", [])
            blocker = failing_twice(runs, now)
            found["qa:" + name] = True if blocker else (False if success_twice(runs) else None)
            latest = runs[0].get("conclusion") or runs[0].get("status") if runs else "no run"
            rows.append(("QA " + name, "BLOCKER: 2 consecutive failures" if blocker else str(latest)))
        except Exception as exc:
            rows.append(("QA " + name, "unknown; API error " + type(exc).__name__))
    for name, days in policy["schedules"].items():
        try:
            wf = api(repository, "actions/workflows/" + name)
            runs = api(repository, "actions/workflows/" + name + "/runs?event=schedule&per_page=10")
            problem = schedule_problem(wf.get("state"), runs.get("workflow_runs", []), days, now)
            found["schedule:" + name] = True if problem else (False if any(r.get("event") == "schedule" and r.get("conclusion") == "success" for r in runs.get("workflow_runs", [])[:1]) else None)
            rows.append(("Scheduled " + name, problem or "configured / within grace"))
        except Exception as exc:
            rows.append(("Scheduled " + name, "unknown; API error " + type(exc).__name__))
    return found, rows


def issue_sync(repository, blockers, now):
    """Schedule-only issue creation/closing; no releases, workflow re-runs or code writes."""
    repo_meta = api(repository, "")
    if not repo_meta.get("has_issues", False):
        return ["Issues disabled; no issue mutation (" + repository + ")"]
    issues = api(repository, "issues?state=all&per_page=100")
    logs = []
    for key, is_bad in blockers.items():
        if is_bad is None:
            continue  # An ambiguous/single-failure result never closes an existing blocker.
        marker = "<!-- portfolio-ops:" + key + " -->"
        matches = [i for i in issues if marker in (i.get("body") or "") and "pull_request" not in i]
        issue = sorted(matches, key=lambda x: x["number"], reverse=True)[0] if matches else None
        if is_bad:
            if issue and issue.get("state") == "open":
                continue
            title = BLOCKER_PREFIX + " " + key + " requires investigation"
            body = (marker + "\nPersistent failure or missed schedule confirmed by the daily GitHub-only "
                    "maintenance check. Do not remove signing, release or security gates. "
                    "See Actions run logs and latest workflow state. "
                    "The issue closes automatically only after confirmed recovery or "
                    "the schedule recovers. Recorded at " + now.isoformat() + ".")
            if issue:
                api(repository, "issues/" + str(issue["number"]), "PATCH", {"state": "open"})
                logs.append("Reopened #" + str(issue["number"]) + " for " + key)
            else:
                created = api(repository, "issues", "POST", {"title": title, "body": body})
                logs.append("Opened #" + str(created["number"]) + " for " + key)
        elif issue and issue.get("state") == "open":
            # Positive state: no current persistent failure or missed schedule.
            api(repository, "issues/" + str(issue["number"]), "PATCH", {"state": "closed"})
            logs.append("Closed recovered #" + str(issue["number"]) + " for " + key)
    return logs


def readiness(repository, policy):
    metadata = api(repository, "")
    branch = api(repository, "branches/main")
    current_sha = branch["commit"]["sha"]
    prs = api(repository, "pulls?state=open&per_page=100")
    releases = api(repository, "releases?per_page=5")
    artifacts = api(repository, "actions/artifacts?per_page=1")
    lines = ["## Release preparation — " + repository, "",
             "**Evidence-only. NOT a production, signing or deployment authorization.**", "",
             "- Main SHA: `" + current_sha + "`",
             "- Open pull requests: " + str(len(prs)),
             "- Dependabot PRs: " + str(sum("dependabot" in ((p.get("user") or {}).get("login") or "").lower() for p in prs)),
             "- Latest published release: " + next((r.get("tag_name", "unknown") for r in releases if not r.get("draft")), "none"),
             "- Actions artifacts (repository total, not billing): " + str(artifacts.get("total_count", "unknown"))]
    stale = False
    for name in policy["qa"]:
        data = api(repository, "actions/workflows/" + name + "/runs?branch=main&per_page=10")
        runs = [x for x in data.get("workflow_runs", []) if x.get("status") == "completed"]
        if not runs:
            lines.append("- " + name + ": NO COMPLETED MAIN RUN")
            stale = True
            continue
        run = runs[0]
        fresh = run.get("head_sha") == current_sha and run.get("conclusion") == "success"
        stale |= not fresh
        lines.append("- " + name + ": " + ("PASS at main SHA" if fresh else "NOT CURRENT/GREEN") +
                     " — run #" + str(run.get("id")))
    if metadata.get("private"):
        lines.append("- Private repository: yes; no data, secrets, logs or APKs uploaded")
    lines.extend(["", "**Human release GO remains mandatory**. Verify product-specific "
                  "device acceptance, latest gated CI, signer continuity, backups, "
                  "immutable release receipts and any Cloudflare Access controls. "
                  "No release tags, signing or deployment actions are executed."])
    if stale:
        lines.append("**Readiness finding:** stale or missing CI evidence; do not publish.")
    return lines


def summarize(lines):
    output = "\n".join(lines) + "\n"
    print(output)
    target = os.environ.get("GITHUB_STEP_SUMMARY")
    if target:
        with open(target, "a", encoding="utf-8") as handle:
            handle.write(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=("health", "health-audit", "release"))
    args = parser.parse_args()
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    owner, _, name = repository.partition("/")
    if owner != "xantic21" or name not in POLICY:
        raise SystemExit("This owner/repository is not on the explicit allowlist")
    if os.environ.get("GITHUB_REF") != "refs/heads/main":
        raise SystemExit("Must run from main")
    if args.mode == "health" and os.environ.get("GITHUB_EVENT_NAME") != "schedule":
        raise SystemExit("Issue updates are allowed only on scheduled events")
    now = datetime.now(timezone.utc)
    policy = POLICY[name]
    if args.mode == "release":
        summarize(readiness(repository, policy))
        return
    blockers, rows = checks(repository, policy, now)
    output = ["## Portfolio operations — " + repository,
              "", "Schedule: daily read/check, issue only for sustained blockers.", ""]
    output.extend("- **" + title + "**: " + value for title, value in rows)
    if args.mode == "health":
        try:
            changes = issue_sync(repository, blockers, now)
            output.extend(["", "### Issue transitions"] + ["- " + x for x in changes] if changes else [])
        except Exception as exc:
            output.append("Issue synchronisation unavailable: " + type(exc).__name__)
    summarize(output)


if __name__ == "__main__":
    main()
