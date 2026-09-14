"""Recommendation and optimization interface domain models."""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, Dict, Any, List

from .common import Location
from .shipment import RoutePoint


class TransportMode(str, Enum):
    """Modes of freight transport."""
    ROAD = "ROAD"
    RAIL = "RAIL"
    AIR = "AIR"
    MARITIME = "MARITIME"
    MULTIMODAL = "MULTIMODAL"


class RecommendationStatus(str, Enum):
    """Decision status for reroute proposals."""
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXECUTED = "EXECUTED"


class RedeploymentUrgency(str, Enum):
    """Urgency grade for asset redeployment."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RedeploymentStatus(str, Enum):
    """Status of an asset redeployment workflow."""
    REQUESTED = "REQUESTED"
    DISPATCHED = "DISPATCHED"
    EN_ROUTE = "EN_ROUTE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


@dataclass
class RouteAlternative:
    """A viable alternative transit route bypassing disruptions."""
    route_id: str
    route_name: str
    path_summary: str
    transport_mode: TransportMode
    distance_km: float
    estimated_transit_hours: float
    risk_score: float  # Scale 0.0 (safe) to 1.0 (high risk)
    estimated_cost_usd: float
    waypoints: List[RoutePoint] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "route_id": self.route_id,
            "route_name": self.route_name,
            "path_summary": self.path_summary,
            "transport_mode": self.transport_mode.value if isinstance(self.transport_mode, TransportMode) else self.transport_mode,
            "distance_km": self.distance_km,
            "estimated_transit_hours": self.estimated_transit_hours,
            "risk_score": self.risk_score,
            "estimated_cost_usd": self.estimated_cost_usd,
            "waypoints": [wp.to_dict() for wp in self.waypoints],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RouteAlternative":
        tmode = TransportMode(data["transport_mode"]) if isinstance(data["transport_mode"], str) else data["transport_mode"]
        waypoints = [RoutePoint.from_dict(wp) if isinstance(wp, dict) else wp for wp in data.get("waypoints", [])]
        return cls(
            route_id=data["route_id"],
            route_name=data["route_name"],
            path_summary=data["path_summary"],
            transport_mode=tmode,
            distance_km=float(data["distance_km"]),
            estimated_transit_hours=float(data["estimated_transit_hours"]),
            risk_score=float(data.get("risk_score", 0.0)),
            estimated_cost_usd=float(data["estimated_cost_usd"]),
            waypoints=waypoints,
        )


@dataclass
class CarrierOption:
    """Alternative carrier capacity quote."""
    carrier_id: str
    carrier_name: str
    transport_mode: TransportMode
    rate_usd: float
    transit_time_hours: float
    reliability_score: float  # Scale 0.0 to 1.0
    capacity_available: bool = True
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "carrier_id": self.carrier_id,
            "carrier_name": self.carrier_name,
            "transport_mode": self.transport_mode.value if isinstance(self.transport_mode, TransportMode) else self.transport_mode,
            "rate_usd": self.rate_usd,
            "transit_time_hours": self.transit_time_hours,
            "reliability_score": self.reliability_score,
            "capacity_available": self.capacity_available,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CarrierOption":
        tmode = TransportMode(data["transport_mode"]) if isinstance(data["transport_mode"], str) else data["transport_mode"]
        return cls(
            carrier_id=data["carrier_id"],
            carrier_name=data["carrier_name"],
            transport_mode=tmode,
            rate_usd=float(data["rate_usd"]),
            transit_time_hours=float(data["transit_time_hours"]),
            reliability_score=float(data.get("reliability_score", 0.9)),
            capacity_available=data.get("capacity_available", True),
            notes=data.get("notes"),
        )


@dataclass
class RerouteRecommendation:
    """AI/optimization recommendation package for mitigating disruption to a shipment."""
    recommendation_id: str
    shipment_id: str
    disruption_id: str
    original_route_summary: str
    alternatives: List[RouteAlternative] = field(default_factory=list)
    carrier_options: List[CarrierOption] = field(default_factory=list)
    recommended_route_id: Optional[str] = None
    recommended_carrier_id: Optional[str] = None
    rationale: str = ""
    delay_hours_saved: float = 0.0
    cost_delta_usd: float = 0.0
    status: RecommendationStatus = RecommendationStatus.PENDING_APPROVAL
    created_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "recommendation_id": self.recommendation_id,
            "shipment_id": self.shipment_id,
            "disruption_id": self.disruption_id,
            "original_route_summary": self.original_route_summary,
            "alternatives": [alt.to_dict() for alt in self.alternatives],
            "carrier_options": [c.to_dict() for c in self.carrier_options],
            "recommended_route_id": self.recommended_route_id,
            "recommended_carrier_id": self.recommended_carrier_id,
            "rationale": self.rationale,
            "delay_hours_saved": self.delay_hours_saved,
            "cost_delta_usd": self.cost_delta_usd,
            "status": self.status.value if isinstance(self.status, RecommendationStatus) else self.status,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RerouteRecommendation":
        status = RecommendationStatus(data["status"]) if isinstance(data["status"], str) else data["status"]
        alts = [RouteAlternative.from_dict(a) if isinstance(a, dict) else a for a in data.get("alternatives", [])]
        carriers = [CarrierOption.from_dict(c) if isinstance(c, dict) else c for c in data.get("carrier_options", [])]
        return cls(
            recommendation_id=data["recommendation_id"],
            shipment_id=data["shipment_id"],
            disruption_id=data["disruption_id"],
            original_route_summary=data["original_route_summary"],
            alternatives=alts,
            carrier_options=carriers,
            recommended_route_id=data.get("recommended_route_id"),
            recommended_carrier_id=data.get("recommended_carrier_id"),
            rationale=data.get("rationale", ""),
            delay_hours_saved=float(data.get("delay_hours_saved", 0.0)),
            cost_delta_usd=float(data.get("cost_delta_usd", 0.0)),
            status=status,
            created_at=data.get("created_at"),
        )


@dataclass
class RedeploymentRequest:
    """Dispatch order to redeploy an idle asset to rescue or support a disrupted shipment."""
    request_id: str
    asset_id: str
    target_shipment_id: str
    origin_location: Location
    target_location: Location
    urgency: RedeploymentUrgency = RedeploymentUrgency.MEDIUM
    status: RedeploymentStatus = RedeploymentStatus.REQUESTED
    estimated_arrival_time: Optional[str] = None
    reason: str = ""
    created_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "asset_id": self.asset_id,
            "target_shipment_id": self.target_shipment_id,
            "origin_location": self.origin_location.to_dict(),
            "target_location": self.target_location.to_dict(),
            "urgency": self.urgency.value if isinstance(self.urgency, RedeploymentUrgency) else self.urgency,
            "status": self.status.value if isinstance(self.status, RedeploymentStatus) else self.status,
            "estimated_arrival_time": self.estimated_arrival_time,
            "reason": self.reason,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RedeploymentRequest":
        urgency = RedeploymentUrgency(data["urgency"]) if isinstance(data["urgency"], str) else data["urgency"]
        status = RedeploymentStatus(data["status"]) if isinstance(data["status"], str) else data["status"]
        origin = Location.from_dict(data["origin_location"]) if isinstance(data["origin_location"], dict) else data["origin_location"]
        target = Location.from_dict(data["target_location"]) if isinstance(data["target_location"], dict) else data["target_location"]
        return cls(
            request_id=data["request_id"],
            asset_id=data["asset_id"],
            target_shipment_id=data["target_shipment_id"],
            origin_location=origin,
            target_location=target,
            urgency=urgency,
            status=status,
            estimated_arrival_time=data.get("estimated_arrival_time"),
            reason=data.get("reason", ""),
            created_at=data.get("created_at"),
        )
