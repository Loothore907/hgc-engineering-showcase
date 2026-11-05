# Provenance and scope

Reviewed source: `Loothore907/homegrown-cannalytics` at commit `907df269739b5edf1c47c072ecc7a7b991c87242` on November 5, 2026.

## Source excerpt

`src/hgc_showcase/routing_core.py` retains the original `EARTH_RADIUS_METERS`, `haversine_meters`, `_distance`, `_route_cost`, `_nearest_neighbor`, and `_two_opt` block from `src/homegrown_cannalytics/routing/optimizer.py`. Function bodies are unchanged. The header, imports and private-review attribution were isolated for this package. The production wrapper is not copied.

The two files under `schemas/v1/` are unchanged copies of the named production schemas at this same commit, with all rights reserved. They are included for portfolio review, not as a promise that the minimal public-facts projection satisfies those full contracts.

The original repository remains private; this standalone publication includes only the selected source described above, with no production Git history.

The browser algorithm lab is a new illustrative implementation of the same nearest-neighbor/2-opt concepts, using fabricated unitless nodes. It is not a production UI or a claim of exact browser/Python equivalence across all inputs. Included tests verify the supplied browser fixture against the Python excerpt.

## Evidence for engineering descriptions

- `README.md`: documented pipeline and comparison-distance limitations.
- `schemas/v1/offer-observation.schema.json`: evidence, dates, source type, explicit verification states.
- `schemas/v1/retail-location-snapshot.schema.json`: versioned location and provenance contract.
- `routing/optimizer.py`: stable ordering, group combinations, provider cost adapter, generated timestamps.
- `tests/test_route_optimizer.py`: existing tests for group representative selection and supplied matrix duration. They were inspected, not run here; this package has its own separately reported tests.

The case study is limited to these selected contracts and functions plus the bridge evidence described below. This review does not certify the entire production system or claim which portions were manually authored by any person.

## HGC bridge reuse

The user identified the bridge used in the event project. The actual `license-directory.json` and `birthday-public.json` exports were inspected on November 5, 2026, along with `packages/homegrown-adapter/license-seed.ts` and its `licenseSeedDirectory` implementation. Original files were read-only.

Source SHA-256 fingerprints:
- Directory: `df30ccfe0bf959d51a1a04e293540f63d794b813c5702e44f8d8959ab328d339`.
- Birthday: `e1a74f959a6cd8bf307f847c1312f0ee1086752c35fc98278a7e707f79e46e65`.
- Sanitized intermediate review: `39cf623fcc38e4364c7b69d73b8073592a68b45ca0336825b234ae0c006584b7`.

Raw source dates are preserved in `data/bridge-review.json`. Directory export is January 20; birthday generation is July 26; bridge capture is October 24, 2026. November 5 is the review date only. There are no row-level birthday claim observation or verification timestamps in this export. Separately, on November 5, the HGC owner confirmed that these are current known valid deals and that this specific list was validated in August 2026. The date is recorded at month precision, with no invented day. `data/deal-validation.json` preserves this supplemental owner context, distinct from the unchanged source exports. Nearly all deals were unchanged from the prior year; many known personally to the owner have remained unchanged for years. No independent current shop or license check was performed for this showcase. Export age alone does not establish that a deal is invalid or expired.

All 41 birthday records join uniquely to the 540-record directory by exact license number, with zero missing or duplicated license keys. The directory contains multiple license types; it is not a list of 540 retail shops. The 499 directory records absent from the birthday export do not establish absence of an offer. Eighteen rejected source records are reported as an aggregate; their individual reasons were not inspected.

The six selected records are the first source-order birthday rows with explicit group-wide or per-location scope. They are not representative. Twenty-one unknown-scope records remain visible in aggregate coverage, with one metadata-only example.

Public names, terms, location IDs, group relationships and the eligibility flag come from the birthday export. The joined directory supplies raw historical license type/status and source-version metadata. Directory IDs use a different identifier scheme; birthday IDs must not be represented as directory IDs. The UI’s directory JSON therefore omits `location_id`.

The final allowlist excludes all street addresses because birthday-address upstream lineage is unresolved, along with coordinates, geometry, provider output, artwork, contacts, credentials, private notes and partnership information. The original claim text is retained verbatim for engineering inspection, with no consumer purchasing/navigation controls.

The existing production and event repositories and bridge originals were not modified. This is an standalone engineering presentation, not a live feed or a new production data pipeline.

## Dependencies

The code sample uses Python's standard library. The static site uses plain HTML, CSS, JavaScript and inline SVG. No dependency tree, external fonts, map library, third-party image, analytics or tracking script is redistributed. This avoids packaging the production application's dependency inventory; it does not change rights on the excerpt or the referenced third-party facts.

