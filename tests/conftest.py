"""Shared test configuration and fixtures"""
import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient for API testing"""
    return TestClient(app)


@pytest.fixture
def sample_activities():
    """Provide a deep copy of activities for each test to ensure isolation"""
    return copy.deepcopy(activities)


@pytest.fixture
def reset_activities(monkeypatch, sample_activities):
    """Reset activities to sample data for each test"""
    monkeypatch.setattr("src.app.activities", sample_activities)
    return sample_activities
