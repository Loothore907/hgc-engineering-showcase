"""Allowlisted showcase view of the existing HGC bridge review.

Input is an already sanitized local bridge review, never a production API.
The adapter does not enrich, geocode, infer current validity, or recommend routes.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

ROW_FIELDS = (
    "location_id", "license_number", "public_name", "observed_claim_text",
    "observed_redemption_scope", "redemption_group_id",
    "observed_publication_eligible", "observed_license_type",
    "observed_license_status", "current_availability", "license_evidence_class",
    "license_source_version",
)
METRIC_FIELDS = (
    "directory_rows", "directory_reported_rejected_count", "birthday_rows",
    "directory_missing_license_keys", "birthday_missing_license_keys",
    "directory_duplicate_license_keys", "birthday_duplicate_license_keys",
    "birthday_joined_rows", "birthday_unmatched_rows", "directory_not_in_birthday",
    "explicit_scope_rows", "sample_rows",
)
SCOPE_VALUES = {"per_location", "group_wide", "unknown"}

def project_bridge(review: dict[str, Any], deal_validation: dict[str, Any] | None = None) -> dict[str, Any]:
    if review.get("schema_version") != "hgc-engineering-review/1":
        raise ValueError("Unsupported bridge review schema")
    raw_metrics = review["metrics"]
    metrics = {key: raw_metrics[key] for key in METRIC_FIELDS}
    for key, value in metrics.items():
        if type(value) is not int or value < 0:
            raise ValueError(f"Invalid count: {key}")
    scopes = dict(raw_metrics["scope_counts"])
    if set(scopes) != SCOPE_VALUES or any(type(v) is not int or v < 0 for v in scopes.values()):
        raise ValueError("Invalid scope coverage")
    if sum(scopes.values()) != metrics["birthday_rows"]:
        raise ValueError("Scope counts do not reconcile")
    if metrics["birthday_joined_rows"] + metrics["birthday_unmatched_rows"] != metrics["birthday_rows"]:
        raise ValueError("Join counts do not reconcile")
    if metrics["directory_not_in_birthday"] + metrics["birthday_joined_rows"] != metrics["directory_rows"]:
        raise ValueError("Directory coverage does not reconcile")
    if scopes["group_wide"] + scopes["per_location"] != metrics["explicit_scope_rows"]:
        raise ValueError("Explicit-scope count does not reconcile")
    if metrics["sample_rows"] > metrics["birthday_rows"]:
        raise ValueError("Sample exceeds source count")
    metrics["scope_counts"] = scopes
    rows = []
    keys = set()
    for raw in review["rows"]:
        row = {key: raw[key] for key in ROW_FIELDS}
        key = row["license_number"]
        if not isinstance(key, str) or not key or key != key.strip() or key in keys:
            raise ValueError("Missing, normalized, or duplicate sample license key")
        keys.add(key)
        if row["observed_redemption_scope"] not in {"per_location", "group_wide"}:
            raise ValueError("The selected sample requires explicit scope")
        if row["current_availability"] != "not_verified":
            raise ValueError("Current validity must not be inferred")
        if row["license_evidence_class"] != "historical_snapshot":
            raise ValueError("Expected historical evidence class")
        if not isinstance(row["observed_claim_text"], str):
            raise ValueError("Claim text must be a string")
        # This source-review flag is not a verdict on the deal. A separate
        # owner validation statement can supplement the unchanged source files.
        row.pop("current_availability")
        row["claim_text_sha256"] = hashlib.sha256(row["observed_claim_text"].encode()).hexdigest()
        rows.append(row)
    if len(rows) != metrics["sample_rows"]:
        raise ValueError("Sample count mismatch")
    directory, birthday = review["sources"]["directory"], review["sources"]["birthday"]
    sources = {
        "directory": {key: directory[key] for key in ("file", "schemaVersion", "exportedAt", "capturedAt", "sha256", "upstream_hash")},
        "birthday": {key: birthday[key] for key in ("file", "schema_version", "catalog_id", "generated_at", "sha256")},
    }
    unknown = review["uncertainty_example"]
    example = {key: unknown[key] for key in ("source", "location_id", "license_number", "observed_redemption_scope", "observed_redemption_group_id", "decision")}
    if example["observed_redemption_scope"] != "unknown":
        raise ValueError("Unknown-scope evidence must stay unknown")
    example["decision"] = "Redemption scope is not inferred; omitted from the explicit-scope sample. Unknown scope does not mean the deal is invalid."
    validation = None
    if deal_validation is not None:
        validation = {key: deal_validation[key] for key in (
            "status", "last_validated_month", "reported_at", "source",
            "scope", "independent_current_check", "context",
        )}
        import datetime
        month = datetime.datetime.strptime(validation["last_validated_month"], "%Y-%m")
        if month.strftime("%Y-%m") != validation["last_validated_month"]:
            raise ValueError("Validation month must use YYYY-MM precision")
        datetime.date.fromisoformat(validation["reported_at"])
        if validation["status"] != "current_known_valid_per_owner" or validation["source"] != "HGC owner":
            raise ValueError("Expected explicit owner validation context")
        if validation["scope"] != "birthday deal list" or validation["independent_current_check"] != "not_performed":
            raise ValueError("Owner report must not become an independent current check")
    return {
        "schema_version": "hgc-showcase-bridge-view/2",
        "purpose": "Public engineering showcase; source lineage and separately attributed owner deal validation.",
        "deal_validation": validation,
        "reviewed_at": review["reviewed_at"],
        "rights_status": "all_rights_reserved",
        "sources": sources,
        "metrics": metrics,
        "selection": {
            "method": review["selection"]["method"],
            "sample_is_representative": False,
            "unknown_scope_rows_not_in_sample": scopes["unknown"],
        },
        "adapter_evidence": {
            "file": review["adapter_findings"]["file"],
            "function": review["adapter_findings"]["function"],
            "observed_behavior": list(review["adapter_findings"]["observed_behavior"]),
            "reuse_boundary": review["adapter_findings"]["reuse_boundary"],
        },
        "exclusions": [
            "All coordinates, geometry and provider-derived output",
            "All street addresses: birthday-address upstream lineage is unresolved",
            "Menus, shopping, navigation, logos and artwork",
            "Personal contacts, private notes, credentials and partnerships",
        ],
        "unknowns": [
            "No row-level claim observation or verification date in the birthday export.",
            "Export, generated and capture timestamps describe file lineage, not deal validation or expiry.",
            "The catalog identifier is not evidence of offer effective dates.",
            "Source publication_eligible is not permission for a new public release.",
            "The 18 rejected directory records are a reported count; individual reject reasons were not reviewed.",
            "The selected six rows are a non-representative explicit-scope sample; 21 unknown-scope records remain in coverage.",
        ],
        "uncertainty_example": example,
        "rows": rows,
    }


def join_bridge_exports(directory: dict[str, Any], birthday: dict[str, Any]) -> list[dict[str, Any]]:
    """Join the two existing exports by exact string license number.

    Fails closed for missing/duplicate keys and preserves source order/terms.
    Only allowlisted historical fields leave this function. The caller selects
    its review sample separately; no selection or routing advice is produced.
    """
    if directory.get("schemaVersion") != "hgc-license-directory/1":
        raise ValueError("Unsupported directory schema")
    if birthday.get("schema_version") != "1.0.0":
        raise ValueError("Unsupported birthday schema")
    directory_rows, birthday_rows = directory["locations"], birthday["locations"]
    if birthday.get("qualified_location_count") != len(birthday_rows):
        raise ValueError("Birthday count mismatch")
    index: dict[str, dict[str, Any]] = {}
    for record in directory_rows:
        key = record["license"]["number"]
        if not isinstance(key, str) or not key or key != key.strip() or key in index:
            raise ValueError("Missing or duplicate directory license key")
        index[key] = record
    seen: set[str] = set()
    joined = []
    for record in birthday_rows:
        key = record["license_number"]
        if not isinstance(key, str) or not key or key != key.strip() or key in seen:
            raise ValueError("Missing or duplicate birthday license key")
        seen.add(key)
        if key not in index:
            raise ValueError(f"Unmatched exact license key: {key}")
        license_record = index[key]
        source = license_record["source"]
        if source["evidenceClass"] != "historical_snapshot":
            raise ValueError("Expected a historical directory snapshot")
        if record["redemption_scope"] not in SCOPE_VALUES:
            raise ValueError("Unknown source scope encoding")
        if not isinstance(record["claim_text"], str) or type(record["publication_eligible"]) is not bool:
            raise ValueError("Invalid claim or publication flag type")
        joined.append({
            "location_id": record["location_id"],  # Birthday identifier, never directory.id.
            "license_number": key,
            "public_name": record["shop_name"],
            "observed_claim_text": record["claim_text"],
            "observed_redemption_scope": record["redemption_scope"],
            "redemption_group_id": record["redemption_group_id"],
            "observed_publication_eligible": record["publication_eligible"],
            "observed_license_type": license_record["license"]["type"],
            "observed_license_status": license_record["license"]["status"],
            "current_availability": "not_verified",
            "license_evidence_class": source["evidenceClass"],
            "license_source_version": source["version"],
        })
    return joined


