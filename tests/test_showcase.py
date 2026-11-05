import itertools
import json
import math
import pathlib
import subprocess
import unittest

from hgc_showcase.demo import distance, nodes, run
from hgc_showcase.routing_core import (
    EARTH_RADIUS_METERS, _distance, _nearest_neighbor, _route_cost, _two_opt, haversine_meters
)

ROOT = pathlib.Path(__file__).resolve().parents[1]

class RoutingTests(unittest.TestCase):
    def test_same_coordinate_zero(self):
        p = {"latitude": 61.2, "longitude": -149.9}
        self.assertEqual(haversine_meters(p, p), 0)

    def test_haversine_symmetric(self):
        a = {"latitude": 61.2, "longitude": -149.9}
        b = {"latitude": 61.3, "longitude": -149.7}
        self.assertAlmostEqual(haversine_meters(a,b), haversine_meters(b,a), places=6)

    def test_quarter_equator(self):
        a = {"latitude": 0, "longitude": 0}
        b = {"latitude": 0, "longitude": 90}
        self.assertAlmostEqual(haversine_meters(a,b), math.pi * EARTH_RADIUS_METERS / 2, places=5)

    def test_dateline_short_crossing(self):
        a = {"latitude": 0, "longitude": 179}
        b = {"latitude": 0, "longitude": -179}
        self.assertAlmostEqual(haversine_meters(a,b), math.radians(2)*EARTH_RADIUS_METERS, places=5)

    def test_antipodal(self):
        a = {"latitude": 0, "longitude": 0}
        b = {"latitude": 0, "longitude": 180}
        self.assertAlmostEqual(haversine_meters(a,b), math.pi*EARTH_RADIUS_METERS, places=5)

    def test_distance_adapter(self):
        a = {"coordinates":{"latitude":0,"longitude":0}}
        b = {"coordinates":{"latitude":0,"longitude":1}}
        self.assertEqual(_distance(a,b),haversine_meters(a["coordinates"],b["coordinates"]))

    def test_empty_route_cost(self):
        self.assertEqual(_route_cost([], distance), 0)

    def test_single_node(self):
        point = nodes()[0]
        self.assertEqual(_nearest_neighbor(point, [], distance), [point])
        self.assertEqual(_route_cost([point], distance), 0)
        self.assertEqual(_two_opt([point], distance), [point])

    def test_two_node_closed_route(self):
        a,b=nodes()[:2]
        self.assertAlmostEqual(_route_cost([a,b],distance),2*distance(a,b))

    def test_stable_tie_break(self):
        origin={"location_id":"A","x":0,"y":0}
        b={"location_id":"B","x":1,"y":0}
        c={"location_id":"C","x":-1,"y":0}
        self.assertEqual(_nearest_neighbor(origin,[c,b],distance)[1]["location_id"],"B")

    def test_nearest_invariant_to_input_permutations(self):
        points=nodes()
        expected=_nearest_neighbor(points[0],points[1:],distance)
        for order in itertools.permutations(points[1:4]):
            self.assertEqual(_nearest_neighbor(points[0],list(order)+points[4:],distance),expected)

    def test_origin_preserved(self):
        pts=nodes()
        route=_two_opt(_nearest_neighbor(pts[0],pts[1:],distance),distance)
        self.assertEqual(route[0],pts[0])

    def test_each_node_exactly_once(self):
        pts=nodes()
        route=_two_opt(_nearest_neighbor(pts[0],pts[1:],distance),distance)
        self.assertCountEqual([p["location_id"] for p in route],[p["location_id"] for p in pts])
        self.assertEqual(len(route),len(pts))

    def test_improvement_non_worsening(self):
        pts=nodes(); before=_nearest_neighbor(pts[0],pts[1:],distance); after=_two_opt(before,distance)
        self.assertLessEqual(_route_cost(after,distance),_route_cost(before,distance))

    def test_fixture_has_real_computed_improvement(self):
        result=run()
        self.assertAlmostEqual(result["nearest_cost"],290.368,places=3)
        self.assertAlmostEqual(result["improved_cost"],229.193,places=3)

    def test_improvement_idempotent(self):
        pts=nodes(); first=_two_opt(_nearest_neighbor(pts[0],pts[1:],distance),distance)
        self.assertEqual(_two_opt(first,distance),first)

    def test_input_not_mutated(self):
        pts=nodes(); snapshot=json.dumps(pts,sort_keys=True)
        _two_opt(_nearest_neighbor(pts[0],pts[1:],distance),distance)
        self.assertEqual(json.dumps(pts,sort_keys=True),snapshot)

    def test_deterministic_fixture_output(self):
        self.assertEqual(run(),run())

    def test_fixture_expected_order(self):
        self.assertEqual(run()["improved_order"],list("AFHEDCBG"))

    def test_browser_fixture_agrees_with_python(self):
        js=ROOT/"site"/"algorithm.js"
        script="const a=require("+json.dumps(str(js))+");const n=a.nearest(a.fixture),b=a.improve(n);console.log(JSON.stringify({nearest:n.map(p=>p.id),best:b.map(p=>p.id),cost:a.cost(b)}));"
        result=json.loads(subprocess.check_output(["node","-e",script],text=True))
        py=run()
        self.assertEqual(result["nearest"],py["nearest_order"])
        self.assertEqual(result["best"],py["improved_order"])
        self.assertAlmostEqual(result["cost"],py["improved_cost"],places=3)

    def test_browser_reverse_input_stable(self):
        js=ROOT/"site"/"algorithm.js"
        script="const a=require("+json.dumps(str(js))+");console.log(JSON.stringify(a.improve(a.nearest(a.fixture.slice().reverse())).map(p=>p.id)));"
        result=json.loads(subprocess.check_output(["node","-e",script],text=True))
        self.assertEqual(result,run()["improved_order"])

class BridgeDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/"data/bridge-review.json").read_text())

    def test_source_counts(self):
        self.assertEqual(self.data["metrics"]["directory_rows"],540)
        self.assertEqual(self.data["metrics"]["birthday_rows"],41)

    def test_all_birthday_keys_join(self):
        m=self.data["metrics"]
        self.assertEqual(m["birthday_joined_rows"],41)
        self.assertEqual(m["birthday_unmatched_rows"],0)
        self.assertEqual(m["directory_duplicate_license_keys"],0)
        self.assertEqual(m["birthday_duplicate_license_keys"],0)

    def test_scope_coverage_is_explicit(self):
        self.assertEqual(self.data["metrics"]["scope_counts"],{"group_wide":11,"per_location":9,"unknown":21})

    def test_unknown_example_not_inferred(self):
        row=self.data["uncertainty_example"]
        self.assertEqual(row["observed_redemption_scope"],"unknown")
        self.assertIsNone(row["observed_redemption_group_id"])
        self.assertNotIn("observed_claim_text",row)

    def test_sample_not_presented_as_representative(self):
        self.assertFalse(self.data["selection"]["sample_is_representative"])
        self.assertEqual(len(self.data["rows"]),6)

    def test_exact_source_dates_preserved(self):
        self.assertEqual(self.data["sources"]["directory"]["exportedAt"],"2026-01-20T22:08:04.28371Z")
        self.assertEqual(self.data["sources"]["directory"]["capturedAt"],"2026-10-24T22:43:30.909Z")
        self.assertEqual(self.data["sources"]["birthday"]["generated_at"],"2026-07-26T09:44:04.758552-08:00")

    def test_owner_validation_separate_from_license_snapshot(self):
        for row in self.data["rows"]:
            self.assertNotIn("current_availability",row)
            self.assertEqual(row["license_evidence_class"],"historical_snapshot")
            self.assertNotIn("effective_from",row)
            self.assertNotIn("verified_at",row)

    def test_last_validated_month_is_owner_sourced(self):
        v=self.data["deal_validation"]
        self.assertEqual(v["last_validated_month"],"2026-08")
        self.assertEqual(v["reported_at"],"2026-11-05")
        self.assertEqual(v["source"],"HGC owner")
        self.assertEqual(v["status"],"current_known_valid_per_owner")
        self.assertEqual(v["scope"],"birthday deal list")
        self.assertEqual(v["independent_current_check"],"not_performed")
        self.assertEqual(v,json.loads((ROOT/"data/deal-validation.json").read_text()))

    def test_copy_separates_validation_from_export_age(self):
        html=(ROOT/"site/index.html").read_text()
        app=(ROOT/"site/app.js").read_text()
        self.assertIn("Last validated August 2026",html)
        self.assertIn("file dates do not indicate deal expiry",html)
        self.assertIn("Current known valid deals",app)
        for stale in ("Historical, not current availability", "Current validity not verified", "Inspecting an old file today does not make its records current", "field('Current availability','Not verified')"):
            self.assertNotIn(stale,html+app)

    def test_no_coordinates_addresses_contacts_or_artwork(self):
        banned={"latitude","longitude","coordinates","geometry","public_address","address","formatted_address","phone","email","logo","image_url","captured_by","verified_by","consumer_id"}
        def walk(value):
            if isinstance(value,dict):
                self.assertFalse(banned.intersection(value))
                for child in value.values():walk(child)
            elif isinstance(value,list):
                for child in value:walk(child)
        walk(self.data)

    def test_exact_terms_fingerprints(self):
        import hashlib
        expected=["784c7014d0257fe4afef25d57202c38d566b4ed2526eba886033ae016357bed8","6f692cdc67c3cbfea4a987c373d844d4dd61dd1045bfc92a6ddcd75086da90f0","6f692cdc67c3cbfea4a987c373d844d4dd61dd1045bfc92a6ddcd75086da90f0","283afa7604f42077dc411dd62c70c4c5f3672837874309a02088a5c00dec5a31","283afa7604f42077dc411dd62c70c4c5f3672837874309a02088a5c00dec5a31","283afa7604f42077dc411dd62c70c4c5f3672837874309a02088a5c00dec5a31"]
        self.assertEqual([hashlib.sha256(r["observed_claim_text"].encode()).hexdigest() for r in self.data["rows"]],expected)

    def test_site_dataset_equals_projection(self):
        raw=(ROOT/"site/facts.js").read_text()
        site=json.loads(raw.removeprefix("window.HGC_DATA = ").rstrip().removesuffix(";"))
        self.assertEqual(site,self.data)

    def test_site_has_no_external_service_calls(self):
        for path in (ROOT/"site").glob("*.js"):
            text=path.read_text()
            for prohibited in ("fetch(","XMLHttpRequest","WebSocket","navigator.geolocation","localStorage"):
                self.assertNotIn(prohibited,text)

    def test_sha256_source_identity(self):
        self.assertEqual(self.data["source_review_sha256"],"39cf623fcc38e4364c7b69d73b8073592a68b45ca0336825b234ae0c006584b7")
        self.assertEqual(self.data["sources"]["directory"]["sha256"],"df30ccfe0bf959d51a1a04e293540f63d794b813c5702e44f8d8959ab328d339")
        self.assertEqual(self.data["sources"]["birthday"]["sha256"],"e1a74f959a6cd8bf307f847c1312f0ee1086752c35fc98278a7e707f79e46e65")

    def test_proprietary_and_third_party_notices_retained(self):
        self.assertIn("All rights reserved",(ROOT/"LICENSE").read_text())
        self.assertTrue((ROOT/"THIRD_PARTY_NOTICES.md").exists())

    def test_original_schemas_are_versioned(self):
        for path in (ROOT/"schemas/v1").glob("*.json"):
            schema=json.loads(path.read_text())
            self.assertFalse(schema["additionalProperties"])
            self.assertEqual(schema["properties"]["schema_version"]["const"],"1.0.0")

class BridgeAdapterTests(unittest.TestCase):
    def setUp(self):
        self.output=json.loads((ROOT/"data/bridge-review.json").read_text())
        # Synthetic construction of the source-review shape; no excluded values.
        self.validation=self.output["deal_validation"]
        for row in self.output["rows"]: row["current_availability"]="not_verified"
        self.review={"schema_version":"hgc-engineering-review/1","metrics":self.output["metrics"],"rows":self.output["rows"],"sources":self.output["sources"],"uncertainty_example":self.output["uncertainty_example"],"reviewed_at":self.output["reviewed_at"],"selection":self.output["selection"],"adapter_findings":self.output["adapter_evidence"]}

    def project(self):
        from hgc_showcase.bridge_view import project_bridge
        return project_bridge(self.review, self.validation)

    def test_projection_deterministic(self):
        self.assertEqual(self.project(),self.project())

    def test_validation_does_not_rewrite_source_dates(self):
        data=self.project()
        self.assertEqual(data["deal_validation"],self.validation)
        self.assertEqual(data["sources"],self.output["sources"])
        self.assertNotIn("current_availability",data["rows"][0])

    def test_no_owner_validation_inferred_without_context(self):
        from hgc_showcase.bridge_view import project_bridge
        self.assertIsNone(project_bridge(self.review)["deal_validation"])

    def test_owner_report_cannot_become_independent_check(self):
        self.validation["independent_current_check"]="performed"
        with self.assertRaises(ValueError):self.project()

    def test_validation_month_does_not_invent_a_day(self):
        self.validation["last_validated_month"]="2026-08-17"
        with self.assertRaises(ValueError):self.project()

    def test_allowlist_drops_unapproved_fields(self):
        self.review["rows"][0].update({"public_address":"synthetic excluded street","coordinates":{"latitude":1,"longitude":2},"email":"excluded@example.invalid"})
        row=self.project()["rows"][0]
        self.assertNotIn("public_address",row)
        self.assertNotIn("coordinates",row)
        self.assertNotIn("email",row)

    def test_rejects_unknown_schema(self):
        self.review["schema_version"]="unexpected"
        with self.assertRaises(ValueError):self.project()

    def test_rejects_duplicate_sample_license(self):
        self.review["rows"][1]["license_number"]=self.review["rows"][0]["license_number"]
        with self.assertRaises(ValueError):self.project()

    def test_rejects_changed_scope_coverage(self):
        self.review["metrics"]["scope_counts"]["unknown"]+=1
        with self.assertRaises(ValueError):self.project()

    def test_rejects_changed_join_coverage(self):
        self.review["metrics"]["birthday_joined_rows"]-=1
        with self.assertRaises(ValueError):self.project()

    def test_rejects_current_availability_claim(self):
        self.review["rows"][0]["current_availability"]="available"
        with self.assertRaises(ValueError):self.project()

    def test_rejects_invented_scope(self):
        self.review["uncertainty_example"]["observed_redemption_scope"]="per_location"
        with self.assertRaises(ValueError):self.project()

    def test_preserves_terms_byte_for_byte(self):
        self.review["rows"][0]["observed_claim_text"]=" Exact source.  Spaces; punctuation\nremain. "
        self.assertEqual(self.project()["rows"][0]["observed_claim_text"]," Exact source.  Spaces; punctuation\nremain. ")

    def test_does_not_mutate_source(self):
        before=json.dumps(self.review,sort_keys=True)
        self.project()
        self.assertEqual(before,json.dumps(self.review,sort_keys=True))

    def test_rejects_boolean_count(self):
        self.review["metrics"]["birthday_rows"]=True
        with self.assertRaises(ValueError):self.project()

class ExactJoinTests(unittest.TestCase):
    def setUp(self):
        self.directory={"schemaVersion":"hgc-license-directory/1","locations":[{"id":"tenant_fixture","name":"Directory label","license":{"number":"001","type":"Fixture type","status":"Historical raw status"},"source":{"evidenceClass":"historical_snapshot","version":"fixture-v2"},"coordinates":{"latitude":12,"longitude":34},"address":"EXCLUDED"}]}
        self.birthday={"schema_version":"1.0.0","qualified_location_count":1,"locations":[{"location_id":"birthday_fixture","license_number":"001","shop_name":"Birthday label","claim_text":" Exact terms. ","redemption_group_id":None,"redemption_scope":"unknown","publication_eligible":False,"address":"EXCLUDED"}]}

    def join(self):
        from hgc_showcase.bridge_view import join_bridge_exports
        return join_bridge_exports(self.directory,self.birthday)

    def test_exact_string_key_preserves_leading_zero(self):
        self.assertEqual(self.join()[0]["license_number"],"001")

    def test_never_fuzzy_matches_license(self):
        self.birthday["locations"][0]["license_number"]="1"
        with self.assertRaises(ValueError):self.join()

    def test_duplicate_directory_key_rejected(self):
        self.directory["locations"].append(self.directory["locations"][0])
        with self.assertRaises(ValueError):self.join()

    def test_duplicate_birthday_key_rejected(self):
        self.birthday["locations"].append(self.birthday["locations"][0]);self.birthday["qualified_location_count"]=2
        with self.assertRaises(ValueError):self.join()

    def test_provider_fields_and_directory_id_excluded(self):
        row=self.join()[0]
        self.assertNotIn("coordinates",row);self.assertNotIn("address",row);self.assertNotIn("id",row)
        self.assertEqual(row["location_id"],"birthday_fixture")
        self.assertEqual(row["public_name"],"Birthday label")

    def test_terms_and_unknown_scope_preserved(self):
        row=self.join()[0]
        self.assertEqual(row["observed_claim_text"]," Exact terms. ")
        self.assertEqual(row["observed_redemption_scope"],"unknown")
        self.assertFalse(row["observed_publication_eligible"])
        self.assertEqual(row["current_availability"],"not_verified")

    def test_count_mismatch_rejected(self):
        self.birthday["qualified_location_count"]=2
        with self.assertRaises(ValueError):self.join()

    def test_schema_mismatch_rejected(self):
        self.directory["schemaVersion"]="unknown"
        with self.assertRaises(ValueError):self.join()

    def test_missing_key_rejected(self):
        self.birthday["locations"][0]["license_number"]=""
        with self.assertRaises(ValueError):self.join()

    def test_sample_unknown_scope_rejected(self):
        helper=BridgeAdapterTests();helper.setUp()
        helper.review["rows"][0]["observed_redemption_scope"]="unknown"
        with self.assertRaises(ValueError):helper.project()

if __name__=="__main__":
    unittest.main()
