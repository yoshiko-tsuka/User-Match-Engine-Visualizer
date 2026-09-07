import math
import time
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from pydantic import BaseModel, Field

app = FastAPI(
    title="User Matching Engine",
    description="Two-stage compatibility gating and ranking API using modern Python",
    version="2.0.0"
)

templates = Jinja2Templates(directory="templates")

# ==========================================
# 1. DATABASE & GRAPH SIMULATION (Mock Read-Only Data)
# ==========================================
MOCK_GRAPH_DB: dict[str, dict] = {
    "user_001": {
        "id": "user_001",
        "preferences": {"min_age": 25, "max_age": 35, "max_distance_km": 50},
        "attributes": {"age": 28, "latitude": -33.8688, "longitude": 151.2093}, # Sydney
        "channels": {
            "professional": [0.85, 0.12, 0.64, 0.05],  # Dense vector embedding
            "interests": ["python", "machine-learning", "hiking", "chess"]
        }
    },
    "user_002": {
        "id": "user_002",
        "preferences": {"min_age": 21, "max_age": 40, "max_distance_km": 100},
        "attributes": {"age": 31, "latitude": -33.8915, "longitude": 151.2767}, # Bondi
        "channels": {
            "professional": [0.79, 0.15, 0.70, 0.01],
            "interests": ["python", "data-science", "surfing", "chess"]
        }
    },
    "user_003": {
        "id": "user_003",
        "preferences": {"min_age": 30, "max_age": 45, "max_distance_km": 10},
        "attributes": {"age": 22, "latitude": -37.8136, "longitude": 144.9631}, # Melbourne
        "channels": {
            "professional": [0.20, 0.90, 0.10, 0.88],
            "interests": ["finance", "cooking"]
        }
    }
}

class ExternalGraphClient:
    """Mock read-only query interface mimicking a Graph DB client."""
    @staticmethod
    def get_user_profile(user_id: str) -> dict | None:
        return MOCK_GRAPH_DB.get(user_id)


# ==========================================
# 2. Pydantic Response Schemas
# ==========================================
class ChannelScores(BaseModel):
    professional_similarity: float
    interests_overlap: float

class MatchResult(BaseModel):
    target_user_id: str
    is_compatible: bool
    compatibility_reason: str
    final_rank_score: float = Field(..., description="Weighted multi-channel score between 0.0 and 1.0")
    channel_breakdown: ChannelScores

class MatchResponse(BaseModel):
    source_user_id: str
    matches: list[MatchResult]
    response_time_ms: float = Field(..., description="Response latency in milliseconds")


# ==========================================
# 3. CORE ARCHITECTURE UTILITIES & LAYERS
# ==========================================
class HaversineMetric:
    """Helper to calculate spatial constraints."""
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0 # Earth's radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

class CompatibilityGate:
    """STAGE 1: Enforces hard bidirectional dealbreakers."""
    @staticmethod
    def evaluate(source: dict, target: dict) -> tuple[bool, str]:
        # Spatial constraint check
        distance = HaversineMetric.calculate_distance(
            source["attributes"]["latitude"], source["attributes"]["longitude"],
            target["attributes"]["latitude"], target["attributes"]["longitude"]
        )
        if distance > source["preferences"]["max_distance_km"]:
            return False, f"Target exceeds source max distance constraint ({distance:.1f}km)."
        if distance > target["preferences"]["max_distance_km"]:
            return False, f"Source exceeds target max distance constraint ({distance:.1f}km)."

        # Age criteria checks
        if not (source["preferences"]["min_age"] <= target["attributes"]["age"] <= source["preferences"]["max_age"]):
            return False, f"Target age ({target['attributes']['age']}) out of source bounds."
        if not (target["preferences"]["min_age"] <= source["attributes"]["age"] <= target["preferences"]["max_age"]):
            return False, f"Source age ({source['attributes']['age']}) out of target bounds."

        return True, "Passed all core compatibility metrics."

class MultiChannelRankingLayer:
    """STAGE 2: Multi-channel weighted similarity score computation."""
    def __init__(self, weights: dict[str, float]):
        self.weights = weights
        # Ensure weights normalize to 1.0
        total_w = sum(weights.values())
        self.normalized_weights = {k: v / total_w for k, v in weights.items()}

    def _cosine_similarity(self, v1: list[float], v2: list[float]) -> float:
        dot_product = sum(a * b for a, b in zip(v1, v2))
        magnitude_v1 = math.sqrt(sum(a * a for a in v1))
        magnitude_v2 = math.sqrt(sum(b * b for b in v2))
        if not magnitude_v1 or not magnitude_v2:
            return 0.0
        return dot_product / (magnitude_v1 * magnitude_v2)

    def _jaccard_similarity(self, list1: list[str], list2: list[str]) -> float:
        set1, set2 = set(list1), set(list2)
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        if not union:
            return 0.0
        return len(intersection) / len(union)

    def rank(self, source: dict, target: dict) -> tuple[float, ChannelScores]:
        # Channel 1: Professional Vector Cosine Similarity
        prof_score = self._cosine_similarity(
            source["channels"]["professional"],
            target["channels"]["professional"]
        )

        # Channel 2: Explicit Interests Jaccard Overlap
        interest_score = self._jaccard_similarity(
            source["channels"]["interests"],
            target["channels"]["interests"]
        )

        # Aggregate using weighted blend
        final_score = (
            (prof_score * self.normalized_weights["professional"]) +
            (interest_score * self.normalized_weights["interests"])
        )

        breakdown = ChannelScores(
            professional_similarity=round(prof_score, 4),
            interests_overlap=round(interest_score, 4)
        )

        return round(final_score, 4), breakdown


# ==========================================
# 4. REST API ENDPOINT
# ==========================================
RANKING_ENGINE = MultiChannelRankingLayer(weights={"professional": 0.60, "interests": 0.40})

@app.get("/api/v1/match", response_model=MatchResponse)
def get_user_matches(
    source_user_id: str = Query(..., description="The ID of the user requesting matching feeds"),
    target_user_ids: list[str] = Query(..., description="List of target user IDs to screen and rank")
):
    start_time = time.perf_counter()
    source_profile = ExternalGraphClient.get_user_profile(source_user_id)
    if not source_profile:
        raise HTTPException(status_code=404, detail=f"Source user '{source_user_id}' not found.")

    results = []

    for target_id in target_user_ids:
        target_profile = ExternalGraphClient.get_user_profile(target_id)
        if not target_profile:
            continue

        # --- STAGE 1: Compatibility Gate ---
        is_compatible, reason = CompatibilityGate.evaluate(source_profile, target_profile)

        if not is_compatible:
            results.append(MatchResult(
                target_user_id=target_id,
                is_compatible=False,
                compatibility_reason=reason,
                final_rank_score=0.0,
                channel_breakdown=ChannelScores(professional_similarity=0.0, interests_overlap=0.0)
            ))
            continue

        # --- STAGE 2: Ranking Layer ---
        rank_score, breakdown = RANKING_ENGINE.rank(source_profile, target_profile)

        results.append(MatchResult(
            target_user_id=target_id,
            is_compatible=True,
            compatibility_reason=reason,
            final_rank_score=rank_score,
            channel_breakdown=breakdown
        ))

    results.sort(key=lambda x: x.final_rank_score, reverse=True)
    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 3)

    return MatchResponse(source_user_id=source_user_id, matches=results, response_time_ms=elapsed_ms)

# ==========================================
# 5. Frontend ENDPOINT
# ==========================================

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )

