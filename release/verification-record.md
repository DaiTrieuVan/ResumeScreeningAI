# Competition Release Verification Record

## Candidate snapshot

- Release candidate: `1.1.0-competition`
- Source snapshot: working tree based on `804b5fb7bdeb30a0993b534b3e6e76010532d50b`
- Verified at: 2026-09-14T12:13:49Z
- Environment: Windows, clean temporary path, Python 3.13, Node.js 24
- Runtime mode: offline; `deterministic-keyword-v1`; Gemini key empty; embedding model disabled
- Status: **internal gates passed**

This is development evidence for the current working tree. It is not the final public-release attestation. After review/commit/merge, rerun `verify_clean_room.ps1 -SourceMode Archive` and replace the commit, tag, CI URL and artifact fields below.

## Automated evidence

| Gate | Result | Evidence |
|---|---|---|
| Release safety | PASS | 236 source files inspected; no tracked secret/PII-risk artifact; synthetic manifest validated |
| Open-source compliance | PASS | 148 code files checked for MIT SPDX header |
| Backend | PASS | 54 pytest tests |
| Frontend components | PASS | 15 Vitest tests |
| Production build | PASS | Vite production bundle generated |
| E2E/showcase | PASS | 7 Playwright journeys, including Blind Review and three-module offline showcase |
| AI benchmark | PASS | 5/5 metrics meet threshold on 30 synthetic CV / 3 JD dataset |
| Clean-room | PASS | 1.44 minutes from a new path, including dependency install and all gates |
| Production npm audit | PASS | 0 production vulnerabilities |
| Full npm audit | PASS | 0 vulnerabilities after Vite/Vitest upgrade |

Machine-readable clean-room step timings are stored in `release/clean-room-result.json`.

## Benchmark lineage

- Dataset: `competition-synthetic` / `competition-v1`
- Release/commit recorded by report: `1.1.0-competition` / `804b5fb`
- Mode/model: offline fallback / `deterministic-offline-v1`
- JSON SHA-256: `F0FD08178A66C0C366CD413847585F74441377FC873A8116C92F01EB7CC93E27`
- Markdown SHA-256: `48CC5DBFE76C91D4085E37E2B7B42C5D3D9AC21648D7022510FE1A4D376EB3B0`

| Metric | Result | Threshold |
|---|---:|---:|
| Mandatory recall | 1.0000 | 0.90 |
| Evidence precision | 1.0000 | 0.90 |
| UNKNOWN accuracy | 1.0000 | 0.95 |
| Ranking agreement | 1.0000 | 0.70 |
| Batch completion | 1.0000 | 1.00 |

## Release assets still requiring final values

- Annotated tag: pending merge to `main`
- Final source archive/checksum: pending tag
- CI run URL: pending push/PR
- Frontend SPDX SBOM and Python `pip freeze`: generate from final clean-room environment
- Demo video/screenshots: pending team selection
- Public GitHub Release URL and submission-form links: pending user-controlled publication

## Known limitations and production boundaries

- Benchmark data is synthetic and deterministic; it validates reproducibility and metric plumbing, not real-world hiring accuracy.
- The competition deployment is single-node with SQLite/local file storage.
- Role headers are prototype authorization; enterprise deployment requires a real identity provider and server policy enforcement.
- Scanned PDFs use manual verified-text recovery; dedicated OCR remains optional.
- Live crawler and external model behavior depend on network/provider state; the supported competition fallback is fully offline.
- AI recommendations never auto-reject a candidate and require human review.
