# Homegrown Cannalytics · Engineering Showcase

A focused look at how HGC turns source records into traceable, reusable views.

This standalone portfolio sample brings together **data modeling, an exact-license bridge, provenance-aware presentation and deterministic route-ordering primitives**. The production repository, infrastructure, operational data and Git history remain private.

## Start here

- **Interactive case study:** download this repository and open [`site/index.html`](site/index.html). It runs locally without a build, account, API key or network services.
- **Data adapter:** [`bridge_view.py`](src/hgc_showcase/bridge_view.py) joins records by exact license number and projects only allowed fields.
- **Algorithm excerpt:** [`routing_core.py`](src/hgc_showcase/routing_core.py) contains selected pure Python distance, nearest-neighbor and 2-opt functions.
- **Contracts:** [`schemas/v1/`](schemas/v1/) separates location snapshots from evidence-backed offer observations.
- **Checks:** [`test_showcase.py`](tests/test_showcase.py) covers data boundaries, deterministic behavior and Python/browser fixture parity.

## What to look for

### One bridge, multiple views

The existing HGC bridge supplies two independent exports. All **41 birthday records** join uniquely to a **540-record directory** by exact string license number. The directory covers multiple license types, not 540 retail shops.

The public sample includes six source-order joined records with explicit redemption scope and one metadata-only example. Full-export coverage remains visible: 11 group-wide, 9 per-location and 21 unknown-scope records. Missing scope is preserved as a missing detail, not treated as an invalid deal. The 499 directory rows absent from the birthday export do not establish that no offer exists.

The reusable adapter rejects duplicate or missing keys instead of fuzzy-matching. A field allowlist keeps the view independent of the original exports and production services.

### Evidence and validation stay attached

**Deals last validated August 2026.** HGC's owner confirms these are current known valid deals. Nearly all were unchanged from the prior year, with many unchanged for years. Future updates may add deals; shop changes or license revocation can affect availability. This showcase does not claim an independent current shop check.

August validation is kept separate from the directory's January 20 export, the birthday file's July 26 generation and the bridge's October 24 capture. Export age is not treated as deal expiry. The selected terms and raw source timestamps are preserved, with source and claim fingerprints.

### Deterministic choices, honest limits

The interactive algorithm lab uses eight **fabricated, unitless points**, not real retail locations. It shows input order, stable nearest-neighbor construction and a 2-opt improvement pass. The origin stays fixed and the tour returns to it.

For the included fixture, computed costs are 306.0 input, 290.4 nearest-neighbor and 229.2 after 2-opt. These are abstract comparison units, not road distance, travel time or business savings. 2-opt is a heuristic, not a global-optimum guarantee.

## Run the checks

Python 3.12+ and Node.js 18+ are sufficient. No package installation is required.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m hgc_showcase.demo
node --check site/app.js
node --check site/algorithm.js
node --check site/facts.js
```

PowerShell:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONPATH = 'src'
python -m unittest discover -s tests -v
python -m hgc_showcase.demo
```

62 isolated tests passed during publication preparation. The full production suite was not run here. See the [validation report](docs/QA_REPORT.md) for the exact checks and limits.

## Publication scope

Included: the presentation, selected pure functions, two original schemas, a small allowlisted data projection, tests and provenance. The sample projection is deliberately narrower than the full production schemas; required coordinate or license fields are not invented to force conformance.

Excluded: production history and services, raw exports, real street addresses, coordinates and provider output, retailer artwork, contacts, credentials and operational notes. There are no shopping, purchasing or real-location navigation controls.

See [provenance](docs/PROVENANCE.md), [publication scope](docs/PUBLICATION_SCOPE.md) and [third-party notices](THIRD_PARTY_NOTICES.md).

**All rights reserved.** These selected files are public for portfolio review. No open-source license is granted; third-party facts and materials retain their own rights. See [LICENSE](LICENSE).
