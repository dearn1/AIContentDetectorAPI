# app/tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'healthy'
    assert 'timestamp' in data


def test_pricing_endpoint():
    """Test pricing endpoint"""
    response = client.get("/api/v1/pricing")
    assert response.status_code == 200
    data = response.json()
    assert 'pricing_tiers' in data
    assert 'free' in data['pricing_tiers']


def test_detect_ai_content():
    """Test AI content detection"""
    payload = {
        "text": "In today's digital age, it is important to note that artificial intelligence has revolutionized content creation. Furthermore, machine learning continues to evolve.",
        "api_key": "test_key_12345"
    }

    response = client.post("/api/v1/detect", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'success'
    assert 'analysis' in data
    assert 'ai_probability' in data['analysis']


def test_detect_short_text():
    """Test detection with text that's too short"""
    payload = {
        "text": "Short text",
        "api_key": "test_key_12345"
    }

    response = client.post("/api/v1/detect", json=payload)
    assert response.status_code == 422  # Validation error


def test_detect_missing_api_key():
    """Test detection without API key"""
    payload = {
        "text": "This is a longer text that meets the minimum character requirement for analysis but has no API key.",
        "api_key": ""
    }

    response = client.post("/api/v1/detect", json=payload)
    assert response.status_code == 401


def test_batch_detection():
    """Test batch detection"""
    payload = {
        "texts": [
            "In conclusion, the research demonstrates significant findings in machine learning.",
            "omg just saw the funniest thing at work today!! 😂😂"
        ],
        "api_key": "test_key_12345"
    }

    response = client.post("/api/v1/detect/batch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'success'
    assert data['total_analyzed'] == 2
