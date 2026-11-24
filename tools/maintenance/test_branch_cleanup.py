"""Network-free regression tests for the self-contained branch-retention policy."""
from datetime import datetime, timedelta, timezone
import os
import unittest
from branch_cleanup import candidate, safe_name

REPO = os.environ.get('GITHUB_REPOSITORY', 'xantic21/stride')
NOW = datetime(2026, 12, 20, tzinfo=timezone.utc)
SHA = 'a' * 40


def branch(name='feat/safe-small-change', sha=SHA, protected=False):
    return {'name': name, 'commit': {'sha': sha}, 'protected': protected}


def pr(name='feat/safe-small-change', sha=SHA, age=15, number=3, merged=True,
       base='main', state='closed', repo=REPO):
    return {'head': {'ref': name, 'sha': sha, 'repo': {'full_name': repo}},
            'base': {'ref': base}, 'number': number, 'state': state,
            'merged_at': (NOW - timedelta(days=age)).isoformat() if merged else None}


class CleanupPolicyTest(unittest.TestCase):
    def valid(self, b=None, prs=None, protected=None):
        return candidate(b or branch(), prs or [pr()], REPO, NOW, protected or set())

    def test_minimum_age(self):
        self.assertIsNone(self.valid(prs=[pr(age=13)]))
        self.assertIsNotNone(self.valid(prs=[pr(age=14)]))

    def test_reused_or_open_branch_is_safe(self):
        self.assertIsNone(self.valid(prs=[pr(), pr(number=4, merged=False)]))
        self.assertIsNone(self.valid(prs=[pr(), pr(number=4, merged=False, state='open')]))

    def test_sha_change_or_tagged_head(self):
        self.assertIsNone(self.valid(b=branch(sha='b' * 40)))
        self.assertIsNone(self.valid(protected={SHA}))

    def test_foreign_pr_and_wrong_base(self):
        self.assertIsNone(self.valid(prs=[pr(repo='other/fork')]))
        self.assertIsNone(self.valid(prs=[pr(base='develop')]))

    def test_git_protected_branch(self):
        self.assertIsNone(self.valid(b=branch(protected=True)))

    def test_sensitive_refs_are_excluded(self):
        for name in ('main', 'release/1.0.1', 'evidence/audit', 'feat/signing',
                     'docs/release-notes', 'feat/one..two', 'fix/abc;rm',
                     'hacc/2.1.0', 'feat/publish-plan', 'approval/device',
                     'feat/integration', 'docs/backup', 'fix/prod-auth',
                     'feat/audit-proof', 'refs/heads/main'):
            with self.subTest(name=name):
                self.assertFalse(safe_name(name))

    def test_regular_merged_work_names_are_allowed(self):
        for name in ('feat/safer-ui', 'fix/icon', 'chore/format',
                     'docs/readme', 'dependabot/npm_and_yarn/one'):
            with self.subTest(name=name):
                self.assertTrue(safe_name(name))


if __name__ == '__main__':
    unittest.main()
