# xantform README standard

**Edition:** 1.0 · 25 November 2026 · Applies to the landing README of every portfolio repository and to current-facing documentation (documentation index, security policy, contribution guide, pull request template). Public copy of the portfolio's README standard; the automated checks (`audit_portfolio.py`) run with the private source.

## 1. Writing rules

- **US English**, sentence-case headings, short declarative sentences. Describe what the product does for a person before how it is built.
- **Only verified facts.** Features, release lines and status must match the actual code, tags and evidence. No invented badges, test results, stars, user numbers, ratings, performance figures or roadmap promises. Owner attestations are labeled as such; open evidence is labeled "not PASS".
- **No filler.** Avoid generic AI phrasing ("seamless", "cutting-edge", "unlock", "elevate", "empower"), repeated claims, exclamation marks and emojis.
- **Names.** Use the approved names (Cremaflux, Yardphase, Orbit, Gatevector, Stride, Endurhythm, hevy2garmin, xantform). A legacy name appears only with its new name on the same line ("Cremaflux (formerly Coffee Lab)", "published as Coffee Lab `android-v2.3.1`"). Technical identifiers — repository names, package and app IDs, tags, Workers, routes, workflow and secret names, file names — stay as they are and are written in code format.
- **Historical records stay as recorded:** dated, versioned, release, audit and evidence documents and verbatim archives are not rewritten.

## 2. Landing README modules (in this order)

| # | Module | Required | Content |
| --- | --- | --- | --- |
| 1 | Hero | yes | `<p align="center"><img src="docs/brand/hero.svg" alt="<Name> — <tagline>" width="100%"></p>` as the first line |
| 2 | Promise | yes | One bold sentence and one plain sentence for a non-technical reader |
| 3 | Name note | while names are new | `<sub>` line: "<Name> is the new name of <old>. Repository, package ID, signing and release tags are unchanged." |
| 4 | Release line | yes | One factual line: latest immutable release (linked tag) · platform · visibility; a short design note ("One UI-inspired") is optional |
| 5 | The experience | yes | A two-column table of benefits plus a short feature list that exists in the current release |
| 6 | Design | yes | Tonal light and tonal dark icons (`docs/brand/icon.svg`, `icon-dark.svg`, width 76), the palette, the design-system link and where native assets are staged |
| 7 | Current release / Current status | yes | Released tag, acceptance basis, material caveats; one line of links to release and evidence |
| 8 | Privacy and reliability | yes (fork: "Project and attribution") | Data boundaries, offline/backup behavior, provider limits |
| 9 | Documentation and development | yes (fork: "Technical reference") | Table of architecture, release, security, quality and historical documents; the xantform design system |
| 10 | License | yes | Private repositories: "Proprietary … no license is granted …"; the fork: upstream license and attribution |
| 11 | Footer | yes | `---` then `<sub>Part of the xantform … portfolio. …</sub>` |

Architecture, installation and development details live in linked documents (for example `docs/README.md`, `INSTALL.md`, the archived technical README) rather than on the landing page.

## 3. Images and accessibility

- Images only from `docs/brand/` (or real product references such as Stride's `design/*.png`); never screenshots with personal data.
- Alt text: "`<Name>` icon: `<motif>`" for icons, "`<Name>` — `<tagline>`" for heroes.
- Hero and icons are SVG masters generated centrally; do not edit copies (see the [design system](DESIGN_SYSTEM.md)).

## 4. Required governance files per repository

| File | Private product repositories | Public fork | Profile repository |
| --- | --- | --- | --- |
| `README.md` | yes | yes | yes |
| `AGENTS.md` with the brand-and-documentation section | yes | — | — |
| `CLAUDE.md` pointing to `AGENTS.md` | yes | — | — |
| Security policy (`SECURITY.md`, `docs/SECURITY.md` or `.github/SECURITY.md`) | yes | yes | — |
| `.github/pull_request_template.md` (shared xantform checklist) | yes | — | — |
| `LICENSE`, `CONTRIBUTING.md` | — | yes (upstream) | — |

## 5. Automated checks (`audit_portfolio.py`)

| Code | Check |
| --- | --- |
| N | Approved names in current-facing documents; legacy names only next to the new name |
| S | Landing README modules 1, 6, 8, 9, 10, 11 and the product name |
| L | Every relative link and image resolves |
| D | Required governance files exist; `CLAUDE.md` points to `AGENTS.md` |
| P | Quoted palette values exist in the registry |
| M | Repository description names the brand and topics include `xantform` (live, read-only) |

Missing checkouts, files or metadata are FAIL. A frozen path (an open release candidate) is reported as EXEMPT only when its freeze is named explicitly.
