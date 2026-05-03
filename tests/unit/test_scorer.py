"""
Unit tests for the Scorer Lambda function.
"""

import pytest
import json

from functions.scorer.lambda_function import (
    lambda_handler,
    calculate_risk_score,
    get_risk_level,
    is_unusual_geography
)


class MockContext:
    """Mock Lambda context."""
    def __init__(self):
        self.request_id = "test-request-456"
        self.function_name = "ScorerFunction"


def get_sample_event(risk_factors=None):
    """Create a sample scored event."""
    event = {
        "source": "custom.security",
        "detail-type": "Suspicious Activity",
        "detail": {
            "eventId": "evt-test-scorer-001",
            "eventType": "UnauthorizedAPICall",
            "timestamp": "2026-05-02T10:15:00Z",
            "sourceIP": "192.168.1.100",
            "user": "test@example.com",
            "result": "FAIL",
            "mfaUsed": True
        }
    }
    
    if risk_factors:
        event["detail"].update(risk_factors)
    
    return event


class TestScorerLambda:
    
    def test_lambda_handler_success(self):
        """Test successful scoring."""
        event = get_sample_event()
        context = MockContext()
        
        result = lambda_handler(event, context)
        
        assert result["statusCode"] == 200
        response = json.loads(result["body"])
        assert "detail" in response
        assert "riskScore" in response["detail"]
        assert "riskLevel" in response["detail"]
    
    def test_calculate_risk_score_normal(self):
        """Test risk score for normal event."""
        detail = {
            "eventType": "ConsoleLogin",
            "result": "SUCCESS",
            "mfaUsed": True
        }
        
        score = calculate_risk_score(detail)
        
        assert isinstance(score, int)
        assert 0 <= score <= 100
        assert score < 50  # Normal event should be low risk
    
    def test_calculate_risk_score_iam_change(self):
        """Test risk score for IAM policy change (high risk)."""
        detail = {
            "eventType": "IAMPolicyChange",
            "result": "SUCCESS",
            "mfaUsed": False  # No MFA for sensitive action
        }
        
        score = calculate_risk_score(detail)
        
        assert score > 50  # Should be medium-high risk
    
    def test_calculate_risk_score_root_access(self):
        """Test risk score for root account access (critical)."""
        detail = {
            "eventType": "ConsoleLogin",
            "user": "root",
            "result": "SUCCESS",
            "mfaUsed": False
        }
        
        score = calculate_risk_score(detail)
        
        assert score > 75  # Should be critical
    
    def test_get_risk_level_low(self):
        """Test risk level LOW."""
        level = get_risk_level(30)
        assert level == "LOW"
    
    def test_get_risk_level_medium(self):
        """Test risk level MEDIUM."""
        level = get_risk_level(55)
        assert level == "MEDIUM"
    
    def test_get_risk_level_high(self):
        """Test risk level HIGH."""
        level = get_risk_level(75)
        assert level == "HIGH"
    
    def test_get_risk_level_critical(self):
        """Test risk level CRITICAL."""
        level = get_risk_level(95)
        assert level == "CRITICAL"
    
    def test_unusual_geography_detection(self):
        """Test detection of unusual geography."""
        detail = {
            "country": "NG",
            "previousLoginCountry": "US",
            "timeSinceLastLogin": "2h"
        }
        
        result = is_unusual_geography(detail)
        
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
