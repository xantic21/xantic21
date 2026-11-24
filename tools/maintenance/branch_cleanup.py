#!/usr/bin/env python3
"""Conservative, repository-local post-merge branch cleanup; HACC stays read-only."""
import argparse
from datetime import datetime, timedelta, timezone
import json
import os
import re
import subprocess

GRACE = timedelta(days=14)
ALLOWED = ('feat/', 'fix/', 'chore/', 'docs/', 'dependabot/')
RESERVED = ('release', 'sign', 'approval', 'evidence', 'cert', 'candidate',
            'audit', 'rollback', 'revert', 'integration', 'backup', 'publish',
            'hacc', 'device', 'prod', 'promote', 'tag', 'record', 'handover')
MAX_REMOVALS = 5


def safe_name(branch):
    """Only trivial work branches, never release/signing/evidence refs."""
    if not isinstance(branch, str) or not re.fullmatch(r'[A-Za-z0-9._/-]+', branch):
        return False
    if '..' in branch or '//' in branch or branch.endswith(('/', '.')):
        return False
    lower = branch.lower()
    return lower.startswith(ALLOWED) and not any(x in lower for x in RESERVED)


def utc_time(value):
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def candidate(branch, prs, repository, now, protected_shas):
    name = branch.get('name')
    sha = (branch.get('commit') or {}).get('sha')
    if (not safe_name(name) or branch.get('protected') is not False or
            not isinstance(sha, str) or not re.fullmatch(r'[a-fA-F0-9]{40}', sha) or
            sha in protected_shas):
        return None
    related = [pr for pr in prs
               if (pr.get('head') or {}).get('ref') == name and
               ((pr.get('head') or {}).get('repo') or {}).get('full_name') == repository]
    if not related or any(pr.get('state') == 'open' for pr in related):
        return None
    # A reused branch with a newer unmerged or too-recent PR is never removed.
    last = max(related, key=lambda pr: pr.get('number', 0))
    merged_at = utc_time(last.get('merged_at'))
    if (not merged_at or now - merged_at < GRACE or now < merged_at or
            (last.get('base') or {}).get('ref') != 'main' or
            (last.get('head') or {}).get('sha') != sha):
        return None
    return {'branch': name, 'sha': sha, 'pr': last['number'], 'merged_at': merged_at}


def gh_items(path):
    raw = subprocess.check_output(
        ['gh', 'api', '--paginate', '--jq', '.[] | @json', path],
        text=True, stderr=subprocess.PIPE)
    return [json.loads(line) for line in raw.splitlines() if line.strip()]


def git_heads():
    raw = subprocess.check_output(['git', 'ls-remote', '--heads', 'origin'], text=True)
    return dict((ref.strip(), sha.strip()) for sha, ref in
                (line.split('\t', 1) for line in raw.splitlines() if '\t' in line))


def git_tag_shas():
    raw = subprocess.check_output(['git', 'ls-remote', '--tags', 'origin'], text=True)
    return {line.split('\t', 1)[0].strip() for line in raw.splitlines() if '\t' in line}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=('audit', 'apply'), default='audit')
    parser.add_argument('--repository', required=True)
    args = parser.parse_args()
    repository = args.repository
    if repository != os.getenv('GITHUB_REPOSITORY') or repository not in {
            'xantic21/coffee-lab', 'xantic21/nfl-pulse', 'xantic21/henning-hub',
            'xantic21/stride', 'xantic21/garmin-chatgpt-cockpit',
            'xantic21/hevy2garmin', 'xantic21/xantic21'}:
        raise SystemExit('Repository identity does not match allowlist; no changes')
    if os.getenv('GITHUB_REF') != 'refs/heads/main':
        raise SystemExit('Not running on main; no changes')
    if args.mode == 'apply' and os.getenv('GITHUB_EVENT_NAME') != 'schedule':
        raise SystemExit('Only the scheduled main-branch workflow can delete refs')
    branches = gh_items(f'repos/{repository}/branches?per_page=100')
    prs = gh_items(f'repos/{repository}/pulls?state=all&per_page=100')
    ref_snapshot = git_heads()
    tags = git_tag_shas()
    protected_shas = {b['commit']['sha'] for b in branches
                      if b.get('protected') or not safe_name(b.get('name'))}
    now = datetime.now(timezone.utc)
    eligible = []
    for branch in branches:
        found = candidate(branch, prs, repository, now, protected_shas | tags)
        if found and ref_snapshot.get('refs/heads/' + found['branch']) == found['sha']:
            eligible.append(found)
    eligible.sort(key=lambda x: (x['merged_at'], x['branch']))
    print(f'Mode={args.mode}; repository={repository}; branches={len(branches)}; eligible={len(eligible)}; max_deletions={MAX_REMOVALS}')
    if len(eligible) > MAX_REMOVALS:
        print(f'Only first {MAX_REMOVALS} eligible refs handled per weekly run')
    deleted = 0
    for item in eligible[:MAX_REMOVALS]:
        name = item['branch']
        sha = item['sha']
        if args.mode == 'audit':
            print(f'ELIGIBLE only: {name} (PR #{item["pr"]}, SHA {sha[:12]})')
            continue
        # Re-read PRs before each deletion; any new open PR vetoes removal.
        current_prs = gh_items(f'repos/{repository}/pulls?state=all&per_page=100')
        original_branch = next((b for b in branches if b['name'] == name), None)
        if not original_branch or candidate(original_branch, current_prs, repository, now, protected_shas | tags) != item:
            print(f'SKIP changed PR state: {name}')
            continue
        # Atomic SHA compare-and-delete: a concurrent push makes the lease fail.
        remote_ref = 'refs/heads/' + name
        if git_heads().get(remote_ref) != sha:
            print(f'SKIP moved ref: {name}')
            continue
        result = subprocess.run(
            ['git', 'push', f'--force-with-lease={remote_ref}:{sha}',
             'origin', ':' + remote_ref], text=True, capture_output=True)
        if result.returncode:
            # Never retry without the lease, and never force-delete a moved ref.
            print(f'SKIP Git rejected leased deletion: {name}: {result.stderr[-500:]}')
            continue
        deleted += 1
        print(f'DELETED {name} (merged PR #{item["pr"]}, SHA {sha[:12]})')
    print(f'Eligible={len(eligible)}; deleted={deleted}; retained={len(branches)-deleted}')


if __name__ == '__main__':
    main()
