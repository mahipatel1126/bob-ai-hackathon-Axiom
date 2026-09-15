"""Comprehensive unit and integration test suite for Chain Guard AI Backend.

Tests all 20 required backend capabilities:
1. Data loading
2. Shipment retrieval
3. Active disruption retrieval
4. Affected shipment detection
5. Shipment -> disruption matching
6. Reroute alternatives
7. Carrier alternatives
8. Fleet redeployment
9. Reefer capability matching
10. Cold-chain normal telemetry
11. Cold-chain excursion detection
12. Severe excursion classification
13. Bob fallback behavior
14. API health endpoint
15. API shipment endpoint
16. API disruption endpoint
17. API reroute endpoint
18. API fleet endpoint
19. API cold-chain endpoint
20. Invalid shipment handling
"""

import unittest
import sys
from pathlib import Path

# Ensure repository root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.backend.services import (
    data_loader,
    disruption_service,
    reroute_service,
    fleet_service,
    cold_chain_service,
    incident_service,
)
from src.backend.bob import default_bob_client
from src.backend.api.router import route_request


class TestChainGuardBackend(unittest.TestCase):
    """Test suite verifying all Chain Guard AI backend components."""

    # 1. Data Loading
    def test_01_data_loading(self):
        shipments = data_loader.get_shipments()
        disruptions = data_loader.get_disruptions()
        fleet = data_loader.get_fleet_assets()
        telemetry = data_loader.get_telemetry()
        self.assertGreaterEqual(len(shipments), 5)
        self.assertGreaterEqual(len(disruptions), 3)
        self.assertGreaterEqual(len(fleet), 6)
        self.assertGreaterEqual(len(telemetry), 15)

    # 2. Shipment Retrieval
    def test_02_shipment_retrieval(self):
        shp = data_loader.get_shipment_by_id("SHP-1001")
        self.assertIsNotNone(shp)
        self.assertEqual(shp["shipment_id"], "SHP-1001")
        self.assertEqual(shp["cargo"]["cargo_type"], "ELECTRONICS")

    # 3. Active Disruption Retrieval
    def test_03_active_disruption_retrieval(self):
        active_disruptions = data_loader.get_disruptions(active_only=True)
        self.assertTrue(all(d.get("is_active", False) for d in active_disruptions))
        dis_ids = [d["disruption_id"] for d in active_disruptions]
        self.assertIn("DIS-2026-001", dis_ids)

    # 4. Affected Shipment Detection
    def test_04_affected_shipment_detection(self):
        affected = disruption_service.get_affected_shipments()
        self.assertGreater(len(affected), 0)
        affected_ids = [a["shipment_id"] for a in affected]
        self.assertIn("SHP-1002", affected_ids)
        self.assertIn("SHP-1003", affected_ids)
        # SHP-1001 is traversing Southwest corridor far from disruptions
        self.assertNotIn("SHP-1001", affected_ids)

    # 5. Shipment -> Disruption Matching
    def test_05_shipment_disruption_matching(self):
        impacts = disruption_service.get_disruptions_for_shipment("SHP-1002")
        self.assertGreaterEqual(len(impacts), 1)
        impact = impacts[0]
        self.assertEqual(impact["disruption_id"], "DIS-2026-001")
        self.assertEqual(impact["urgency"], "IMMEDIATE")
        self.assertTrue(impact["is_cold_chain"])
        self.assertLessEqual(impact["impact_distance_km"], impact["impact_radius_km"])

    # 6. Reroute Alternatives
    def test_06_reroute_alternatives(self):
        alts = reroute_service.find_route_alternatives("SHP-1002")
        self.assertGreater(len(alts), 0)
        rec = reroute_service.generate_reroute_recommendation("SHP-1002")
        self.assertIsNotNone(rec.get("recommended_route_id"))
        self.assertIn(rec["source"], ("deterministic_backend_fallback", "person_2_ai_optimizer"))

    # 7. Carrier Alternatives
    def test_07_carrier_alternatives(self):
        carriers = reroute_service.find_carrier_alternatives()
        self.assertGreater(len(carriers), 0)
        carrier_names = [c["carrier_name"] for c in carriers]
        self.assertTrue(any("Vanguard" in name for name in carrier_names))

    # 8. Fleet Redeployment
    def test_08_fleet_redeployment(self):
        candidates = fleet_service.find_redeployment_candidates_for_shipment("SHP-1002")
        self.assertGreater(len(candidates), 0)
        top = candidates[0]
        self.assertTrue(top["is_fully_compatible"])
        self.assertTrue(top["distance_km"] < 600.0)

    # 9. Reefer Capability Matching
    def test_09_reefer_capability_matching(self):
        # SHP-1002 is cold chain, candidate assets must be reefers
        candidates = fleet_service.find_redeployment_candidates_for_shipment("SHP-1002")
        compatible_reefers = [c for c in candidates if c["is_fully_compatible"]]
        self.assertGreater(len(compatible_reefers), 0)
        for cand in compatible_reefers:
            self.assertTrue(cand["reefer_match"])

    # 10. Cold-Chain Normal Telemetry
    def test_10_cold_chain_normal_telemetry(self):
        # SHP-1001 is non-refrigerated dry cargo
        report_dry = cold_chain_service.analyze_shipment_cold_chain("SHP-1001")
        self.assertFalse(report_dry["is_cold_chain"])
        self.assertFalse(report_dry["excursion_detected"])
        self.assertEqual(report_dry["compliance_status"], "COMPLIANT")

    # 11. Cold-Chain Excursion Detection
    def test_11_cold_chain_excursion_detection(self):
        # SHP-1002 experiences minor transient excursion
        report = cold_chain_service.analyze_shipment_cold_chain("SHP-1002")
        self.assertTrue(report["is_cold_chain"])
        self.assertTrue(report["excursion_detected"])
        self.assertIn(report["severity"], ("MINOR", "MODERATE", "WARNING"))

    # 12. Severe Excursion Classification
    def test_12_severe_excursion_classification(self):
        # SHP-1005 suffers compressor failure up to 18.2 C
        report = cold_chain_service.analyze_shipment_cold_chain("SHP-1005")
        self.assertTrue(report["is_cold_chain"])
        self.assertTrue(report["excursion_detected"])
        self.assertEqual(report["severity"], "CRITICAL")
        self.assertEqual(report["compliance_status"], "NON_COMPLIANT_QUARANTINE")
        self.assertIn("FDA 21 CFR 211", report["regulatory_framework"])

    # 13. Bob Fallback Behavior
    def test_13_bob_fallback_behavior(self):
        briefing = default_bob_client.generate_incident_briefing("SHP-1002")
        self.assertIsNotNone(briefing)
        self.assertEqual(briefing["source"], "local_fallback_engine")
        self.assertFalse(briefing["bob_connected"])
        self.assertTrue(briefing["is_simulated"])
        self.assertIn("recommended_actions", briefing)

    # 14. API Health Endpoint
    def test_14_api_health_endpoint(self):
        status, data = route_request("GET", "/api/health")
        self.assertEqual(status, 200)
        self.assertEqual(data["status"], "healthy")

    # 15. API Shipment Endpoint
    def test_15_api_shipment_endpoint(self):
        status, data = route_request("GET", "/api/shipments/SHP-1002")
        self.assertEqual(status, 200)
        self.assertEqual(data["shipment"]["shipment_id"], "SHP-1002")

    # 16. API Disruption Endpoint
    def test_16_api_disruption_endpoint(self):
        status, data = route_request("GET", "/api/disruptions/affected-shipments")
        self.assertEqual(status, 200)
        self.assertGreater(data["total_affected"], 0)

    # 17. API Reroute Endpoint
    def test_17_api_reroute_endpoint(self):
        status, data = route_request("GET", "/api/reroute/SHP-1003")
        self.assertEqual(status, 200)
        self.assertEqual(data["shipment_id"], "SHP-1003")
        self.assertIsNotNone(data["recommended_route_id"])

    # 18. API Fleet Endpoint
    def test_18_api_fleet_endpoint(self):
        status, data = route_request("GET", "/api/fleet/redeployment?shipment_id=SHP-1002")
        self.assertEqual(status, 200)
        self.assertGreater(data["candidates_count"], 0)

    # 19. API Cold-Chain Endpoint
    def test_19_api_cold_chain_endpoint(self):
        status, data = route_request("GET", "/api/cold-chain/SHP-1005")
        self.assertEqual(status, 200)
        self.assertEqual(data["severity"], "CRITICAL")
        self.assertEqual(data["compliance_status"], "NON_COMPLIANT_QUARANTINE")

    # 20. Invalid Shipment Handling
    def test_20_invalid_shipment_handling(self):
        status, data = route_request("GET", "/api/shipments/INVALID_SHIPMENT_ID_999")
        self.assertEqual(status, 404)
        self.assertIn("error", data)


if __name__ == "__main__":
    unittest.main()
