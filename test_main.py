import pytest
from fastapi.testclient import TestClient
from main import (
    app,
    HaversineMetric,
    CompatibilityGate,
    MultiChannelRankingLayer,
    MOCK_GRAPH_DB,
)

client = TestClient(app)


def test_haversine_same_location():
    # Distance from Sydney to Sydney should be 0.0 km
    distance = HaversineMetric.calculate_distance(
        -33.8688, 151.2093, -33.8688, 151.2093
    )
    assert round(distance, 2) == 0.0


def test_haversine_sydney_to_bondi():
    # Distance between Sydney CBD and Bondi Beach is ~6-7 km
    distance = HaversineMetric.calculate_distance(
        -33.8688, 151.2093, -33.8915, 151.2767
    )
    assert 5.0 < distance < 10.0


def test_compatibility_gate_pass():
    source = MOCK_GRAPH_DB["user_001"]
    target = MOCK_GRAPH_DB["user_002"]
    is_compatible, reason = CompatibilityGate.evaluate(source, target)
    assert is_compatible is True
    assert "Passed" in reason


def test_compatibility_gate_fail_distance():
    source = MOCK_GRAPH_DB["user_001"]  # Max distance 50km
    target = MOCK_GRAPH_DB["user_003"]  # Melbourne (~700km away)
    is_compatible, reason = CompatibilityGate.evaluate(source, target)
    assert is_compatible is False
    assert "distance constraint" in reason


def test_multi_channel_ranking_layer():
    ranking = MultiChannelRankingLayer(weights={"professional": 0.6, "interests": 0.4})
    source = MOCK_GRAPH_DB["user_001"]
    target = MOCK_GRAPH_DB["user_002"]
    final_score, breakdown = ranking.rank(source, target)

    assert 0.0 <= final_score <= 1.0
    assert 0.0 <= breakdown.professional_similarity <= 1.0
    assert 0.0 <= breakdown.interests_overlap <= 1.0


def test_index_route():
    response = client.get("/")
    assert response.status_code == 200
    assert "Matching Engine Visualizer" in response.text


def test_match_api_success():
    response = client.get(
        "/api/v1/match?source_user_id=user_001&target_user_ids=user_002"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["source_user_id"] == "user_001"
    assert len(data["matches"]) == 1
    assert data["matches"][0]["target_user_id"] == "user_002"
    assert data["matches"][0]["is_compatible"] is True


def test_match_api_user_not_found():
    response = client.get(
        "/api/v1/match?source_user_id=non_existent_user&target_user_ids=user_002"
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
