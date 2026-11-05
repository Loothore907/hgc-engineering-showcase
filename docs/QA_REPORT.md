# Validation report

Validated November 5, 2026. Selected public portfolio sample.

## Passed
- 62 Python standard-library tests, including JavaScript/Python fixture parity invoked with Node.js.
- JavaScript syntax checks for app.js, algorithm.js and facts.js.
- Bridge overview, exact license joins, six preserved source records and metadata-only unknown-scope example are included. Source review compared all six records, timestamps and hashes against the actual bridge exports.
- Tab switching retains the same license selection. Directory evidence and birthday evidence display their separate exact source dates. Deal-terms disclosure opens with verbatim source terms.
- Input order, nearest-neighbor and 2-opt stage switching; repeated clicks; deterministic shuffle and restore.
- Browser computed fixture costs: 306.0 input, 433.8 shuffled input, 290.4 nearest-neighbor, 229.2 improved abstract units. These are synthetic calculations, not real-world performance claims.
- Desktop visual inspection, plus responsive-layout inspection in 390 px and 320 px iframe viewports. These are responsive previews, not physical-device tests.
- Unknown-scope example remains unknown across tab changes; birthday IDs are absent from directory evidence JSON. Keyboard tab switching and selected-record focus retention verified.
- No desktop horizontal overflow at the tested viewport.
- Scoped file inventory and targeted secret-pattern review; no production integrations, credentials or personal contact fields found in the packaged files.

## November 5 freshness correction
- Added “Last validated August 2026” and the owner’s confirmation that the list contains current known valid deals.
- Kept January directory export, July file generation and October bridge capture separate from August validation. Source dates, original deal terms and source hashes are unchanged.
- Replaced the blanket current-validity warning with attributed owner validation; no independent current shop/license check is claimed.
- Added regression coverage for month-only validation, owner attribution, no inferred validation without explicit context, and rejection of an invented independent check.

## Limits
- The full production test suite was not run. Passing this isolated sample does not certify production.
- The reusable exact-license join helper was tested with synthetic source-shaped fixtures; actual export join metrics and sample values were verified separately against the original files.
- A transient browser automation timeout was resolved by re-reading the page and retrying the affected inspection; final unknown-scope and directory-ID checks passed.
- Mobile views were visually inspected at responsive widths, not tested on actual iOS/Android devices. Browser tooling could not inspect iframe document metrics, so no programmatic mobile-overflow result is claimed.
- Browser log results contained extension metadata errors, not application exceptions. This is not a cross-browser certification.
- The original bridge exports establish their captured fields. The owner separately confirms the list as current known valid deals, last validated August 2026. This showcase does not claim an independent current shop/license check or a legal determination of redistribution rights. Export age is not treated as deal expiry.
- The website is self-contained and uses no production API calls or external assets. The synthetic algorithm diagram is not street navigation.

## Reproduce

From the extracted kit:

    PYTHONPATH=src python -m unittest discover -s tests -v
    node --check site/app.js
    node --check site/algorithm.js
    node --check site/facts.js

Python 3.12 and Node.js 18+ are required for the full check set.
