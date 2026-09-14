"""Fleet redeployment optimization engine using OR-Tools and robust assignment heuristics."""

from typing import Dict, List, Optional, Tuple
from src.ai.config import AIConfig, DEFAULT_CONFIG
from src.ai.fleet import filter_suitable_vehicles
from src.ai.schemas import (
    FleetAsset,
    FleetAssignment,
    FleetOptimizationResult,
    PriorityLevel,
    Shipment,
    VehicleType,
)


def _estimate_spatial_distance_km(loc1: str, loc2: str) -> float:
    """Deterministic distance estimate between major logistical hubs in km."""
    l1 = loc1.strip().lower()
    l2 = loc2.strip().lower()
    if l1 == l2:
        return 15.0  # Intra-city transit

    # Standard representative inter-city distances (km)
    hub_matrix = {
        ("mumbai", "pune"): 150.0,
        ("mumbai", "nashik"): 165.0,
        ("mumbai", "surat"): 280.0,
        ("mumbai", "ahmedabad"): 525.0,
        ("mumbai", "delhi"): 1420.0,
        ("mumbai", "bengaluru"): 980.0,
        ("delhi", "jaipur"): 280.0,
        ("delhi", "chandigarh"): 240.0,
        ("delhi", "agra"): 210.0,
        ("delhi", "lucknow"): 550.0,
        ("bengaluru", "chennai"): 350.0,
        ("bengaluru", "hyderabad"): 570.0,
        ("chennai", "hyderabad"): 630.0,
        ("kolkata", "bhubaneswar"): 440.0,
        ("kolkata", "patna"): 580.0,
        ("indore", "bhopal"): 195.0,
        ("indore", "mumbai"): 585.0,
    }

    # Symmetrical lookup
    if (l1, l2) in hub_matrix:
        return hub_matrix[(l1, l2)]
    if (l2, l1) in hub_matrix:
        return hub_matrix[(l2, l1)]

    # Hash-based deterministic distance for unlisted pairs (between 100km and 900km)
    hash_val = abs(hash(f"{l1}_{l2}")) % 800 + 100
    return float(hash_val)


def _calculate_assignment_score(
    shipment: Shipment,
    vehicle: FleetAsset,
    distance_km: float,
    config: AIConfig,
) -> Tuple[float, float, float]:
    """Calculate matching benefit score, redeployment cost, and projected utilization gain.
    
    Higher benefit_score = superior match.
    """
    w = config.opt_weights

    # Cost to relocate idle vehicle to shipment origin
    relocation_cost = distance_km * vehicle.cost_per_km

    # Utilization improvement
    # Assigning an idle/underutilized vehicle to a shipment boosts its utilization
    capacity_ratio = min(1.0, shipment.weight_kg / max(1.0, vehicle.capacity_kg))
    util_gain = (1.0 - vehicle.current_utilization) * capacity_ratio
    projected_util = min(1.0, vehicle.current_utilization + util_gain)

    # Priority multiplier
    priority_weights = {
        PriorityLevel.CRITICAL: 1.5,
        PriorityLevel.HIGH: 1.25,
        PriorityLevel.MEDIUM: 1.0,
        PriorityLevel.LOW: 0.8,
    }
    p_weight = priority_weights.get(shipment.priority, 1.0)

    # Benefit formula (normalized 0 to 100)
    # Distance penalty: 0 penalty at 0km, high penalty above 500km
    distance_norm = max(0.0, 1.0 - (distance_km / 800.0))
    # Cost penalty: normalized up to INR 25,000
    cost_norm = max(0.0, 1.0 - (relocation_cost / 25000.0))
    # Utilization reward: higher reward for rescuing lower utilized vehicles
    util_norm = util_gain

    raw_score = (
        (distance_norm * 40.0) +
        (cost_norm * 30.0) +
        (util_norm * 30.0)
    ) * p_weight

    benefit_score = round(max(1.0, min(100.0, raw_score)), 1)
    return benefit_score, relocation_cost, util_gain


def optimize_fleet_redeployment(
    at_risk_shipments: List[Shipment],
    available_fleet: List[FleetAsset],
    config: Optional[AIConfig] = None,
) -> FleetOptimizationResult:
    """Solve global fleet redeployment matching problem to reallocate idle assets to disrupted shipments.
    
    Attempts OR-Tools Linear Solver assignment first; falls back cleanly to greedy heuristic.
    """
    cfg = config or DEFAULT_CONFIG

    if not at_risk_shipments:
        return FleetOptimizationResult(
            assignments=[],
            unassigned_shipments=[],
            unused_vehicles=[v.vehicle_id for v in available_fleet],
            total_redeployment_cost=0.0,
            average_utilization_improvement=0.0,
            optimization_method="No at-risk shipments requiring redeployment.",
            explanation="No at-risk shipments provided. Fleet operations remain nominal.",
        )

    if not available_fleet:
        return FleetOptimizationResult(
            assignments=[],
            unassigned_shipments=[s.shipment_id for s in at_risk_shipments],
            unused_vehicles=[],
            total_redeployment_cost=0.0,
            average_utilization_improvement=0.0,
            optimization_method="No fleet assets available.",
            explanation="No fleet assets available in network for redeployment.",
        )

    # Sort shipments by priority (CRITICAL and HIGH first)
    priority_order = {
        PriorityLevel.CRITICAL: 0,
        PriorityLevel.HIGH: 1,
        PriorityLevel.MEDIUM: 2,
        PriorityLevel.LOW: 3,
    }
    sorted_shipments = sorted(
        at_risk_shipments,
        key=lambda s: priority_order.get(s.priority, 2)
    )

    # Try OR-Tools MILP Assignment
    try:
        from ortools.linear_solver import pywraplp
        solver = pywraplp.Solver.CreateSolver("SCIP")
        if solver:
            result = _solve_ortools_assignment(sorted_shipments, available_fleet, solver, cfg)
            if result is not None:
                return result
    except Exception:
        pass  # Fall back to heuristic

    # Robust Fallback: Priority-weighted Greedy Matching
    return _solve_heuristic_assignment(sorted_shipments, available_fleet, cfg)


def _solve_ortools_assignment(
    shipments: List[Shipment],
    fleet: List[FleetAsset],
    solver,
    config: AIConfig,
) -> Optional[FleetOptimizationResult]:
    """OR-Tools Integer Programming model for maximum benefit asset-to-shipment assignment."""
    n_shipments = len(shipments)
    n_fleet = len(fleet)

    # Variables: x[i, j] = 1 if shipment i assigned to vehicle j
    x = {}
    pair_scores: Dict[Tuple[int, int], Tuple[float, float, float, float]] = {}

    for i, shp in enumerate(shipments):
        suitable_vehicles, _ = filter_suitable_vehicles(shp, fleet, config)
        suitable_ids = {v.vehicle_id for v in suitable_vehicles}

        for j, veh in enumerate(fleet):
            if veh.vehicle_id in suitable_ids:
                x[i, j] = solver.BoolVar(f"x_{i}_{j}")
                origin_loc = shp.current_location or shp.origin
                dist = _estimate_spatial_distance_km(veh.current_location, origin_loc)
                score, cost, util_gain = _calculate_assignment_score(shp, veh, dist, config)
                pair_scores[(i, j)] = (score, cost, util_gain, dist)

    if not x:
        return None  # No valid pairs

    # Constraints:
    # 1. Each shipment assigned to at most 1 vehicle
    for i in range(n_shipments):
        solver.Add(solver.Sum([x[i, j] for j in range(n_fleet) if (i, j) in x]) <= 1)

    # 2. Each vehicle assigned to at most 1 shipment
    for j in range(n_fleet):
        solver.Add(solver.Sum([x[i, j] for i in range(n_shipments) if (i, j) in x]) <= 1)

    # Objective: Maximize total matching benefit score
    objective = solver.Objective()
    for (i, j), var in x.items():
        score = pair_scores[(i, j)][0]
        objective.SetCoefficient(var, score)
    objective.SetMaximization()

    status = solver.Solve()
    if status not in (solver.OPTIMAL, solver.FEASIBLE):
        return None

    assignments: List[FleetAssignment] = []
    assigned_shp_ids = set()
    assigned_veh_ids = set()
    total_cost = 0.0
    total_util_gain = 0.0

    for (i, j), var in x.items():
        if var.solution_value() > 0.5:
            shp = shipments[i]
            veh = fleet[j]
            score, cost, util_gain, dist = pair_scores[(i, j)]
            proj_util = min(1.0, veh.current_utilization + util_gain)

            reason = (
                f"Assigned {veh.vehicle_type.value} ({veh.vehicle_id}) located at {veh.current_location} "
                f"to {shp.cargo_type.value} shipment {shp.shipment_id} at {shp.origin}. "
                f"Deadhead distance: {dist:.0f} km, Relocation cost: INR {cost:,.0f}, "
                f"Utilization gain: +{util_gain * 100:.1f}%."
            )

            assignments.append(FleetAssignment(
                vehicle_id=veh.vehicle_id,
                vehicle_type=veh.vehicle_type,
                shipment_id=shp.shipment_id,
                origin_distance_km=round(dist, 1),
                redeployment_cost=round(cost, 2),
                current_utilization=round(veh.current_utilization, 3),
                projected_utilization=round(proj_util, 3),
                utilization_improvement=round(util_gain, 3),
                benefit_score=score,
                reason=reason,
            ))
            assigned_shp_ids.add(shp.shipment_id)
            assigned_veh_ids.add(veh.vehicle_id)
            total_cost += cost
            total_util_gain += util_gain

    unassigned_shps = [s.shipment_id for s in shipments if s.shipment_id not in assigned_shp_ids]
    unused_vehs = [v.vehicle_id for v in fleet if v.vehicle_id not in assigned_veh_ids]
    avg_gain = (total_util_gain / len(assignments)) if assignments else 0.0

    explanation = (
        f"Optimized redeployment matched {len(assignments)} vehicle(s) to at-risk shipment(s). "
        f"Total deadhead cost: INR {total_cost:,.0f}. Average asset utilization gain: +{avg_gain * 100:.1f}%."
    )

    return FleetOptimizationResult(
        assignments=assignments,
        unassigned_shipments=unassigned_shps,
        unused_vehicles=unused_vehs,
        total_redeployment_cost=round(total_cost, 2),
        average_utilization_improvement=round(avg_gain, 3),
        optimization_method="OR-Tools SCIP Mixed-Integer Linear Programming",
        explanation=explanation,
    )


def _solve_heuristic_assignment(
    shipments: List[Shipment],
    fleet: List[FleetAsset],
    config: AIConfig,
) -> FleetOptimizationResult:
    """Greedy priority matching heuristic."""
    available_veh_pool = {v.vehicle_id: v for v in fleet}
    assignments: List[FleetAssignment] = []
    unassigned_shps: List[str] = []
    total_cost = 0.0
    total_util_gain = 0.0

    for shp in shipments:
        candidates = list(available_veh_pool.values())
        suitable, _ = filter_suitable_vehicles(shp, candidates, config)
        if not suitable:
            unassigned_shps.append(shp.shipment_id)
            continue

        scored_candidates = []
        origin_loc = shp.current_location or shp.origin
        for veh in suitable:
            dist = _estimate_spatial_distance_km(veh.current_location, origin_loc)
            score, cost, util_gain = _calculate_assignment_score(shp, veh, dist, config)
            scored_candidates.append((score, dist, cost, util_gain, veh))

        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        best_score, best_dist, best_cost, best_util_gain, best_veh = scored_candidates[0]

        proj_util = min(1.0, best_veh.current_utilization + best_util_gain)
        reason = (
            f"Assigned {best_veh.vehicle_type.value} ({best_veh.vehicle_id}) stationed at {best_veh.current_location} "
            f"to shipment {shp.shipment_id} at {origin_loc}. Proximity: {best_dist:.0f} km, "
            f"Relocation cost: INR {best_cost:,.0f}, Expected utilization improvement: +{best_util_gain * 100:.1f}%."
        )

        assignments.append(FleetAssignment(
            vehicle_id=best_veh.vehicle_id,
            vehicle_type=best_veh.vehicle_type,
            shipment_id=shp.shipment_id,
            origin_distance_km=round(best_dist, 1),
            redeployment_cost=round(best_cost, 2),
            current_utilization=round(best_veh.current_utilization, 3),
            projected_utilization=round(proj_util, 3),
            utilization_improvement=round(best_util_gain, 3),
            benefit_score=best_score,
            reason=reason,
        ))

        # Remove assigned vehicle from pool
        del available_veh_pool[best_veh.vehicle_id]
        total_cost += best_cost
        total_util_gain += best_util_gain

    unused_vehs = list(available_veh_pool.keys())
    avg_gain = (total_util_gain / len(assignments)) if assignments else 0.0

    explanation = (
        f"Greedy optimization assigned {len(assignments)} asset(s) to urgent shipment(s). "
        f"Total redeployment cost: INR {total_cost:,.0f}. Average asset utilization gain: +{avg_gain * 100:.1f}%."
    )

    return FleetOptimizationResult(
        assignments=assignments,
        unassigned_shipments=unassigned_shps,
        unused_vehicles=unused_vehs,
        total_redeployment_cost=round(total_cost, 2),
        average_utilization_improvement=round(avg_gain, 3),
        optimization_method="Greedy Multi-Objective Assignment Heuristic",
        explanation=explanation,
    )
