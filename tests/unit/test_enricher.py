"""
Unit tests for the Enricher Lambda function.
"""

import pytest
import json

from functions.enricher.lambda_function import (
    lambda_handler,
    enrich_geolocation,
    enrich_account,
    is_unusual_location
)


class MockContext:
    """Mock Lambda context."""
    def __init__(self):
        self.request_id = "test-request-123"
        self.function_name = "TestFunction"


def get_sample_event():
    """Create a sample security event."""
    return {
        "source": "custom.security",
        "detail-type": "Suspicious Activity",
        "detail": {
            "eventId": "evt-test-001",
            "eventType": "UnauthorizedAPICall",
            "timestamp": "2026-05-02T10:15:00Z",
            "sourceIP": "192.168.1.100",
            "user": "test@example.com",
            "accountId": "123456789012",
            "region": "us-east-1",
            "action": "DeleteDBInstance",
            "result": "FAIL"
        }
    }


class TestEnricherLambda:
    
    def test_lambda_handler_success(self):
        """Test successful enrichment."""
        event = get_sample_event()
        context = MockContext()
        
        result = lambda_handler(event, context)
        
        assert result["statusCode"] == 200
        response = json.loads(result["body"])
        assert "enrichment" in response
        assert "requestId" in response["enrichment"]
    
    def test_invalid_event(self):
        """Test with invalid event (missing required fields)."""
        event = {
            "source": "custom.security",
            "detail-type": "Suspicious Activity",
            "detail": {
                # Missing eventId
                "eventType": "UnauthorizedAPICall"
            }
        }
        context = MockContext()
        
        result = lambda_handler(event, context)
        
        assert result["statusCode"] == 400
        assert "error" in json.loads(result["body"])
    
    def test_enrich_geolocation(self):
        """Test geolocation enrichment."""
        detail = {
            "sourceIP": "192.168.1.100",
            "country": "US",
            "region": "us-east-1"
        }
        
        enrichment = enrich_geolocation(detail)
        
        assert enrichment["sourceIP"] == "192.168.1.100"
        assert enrichment["country"] == "US"
    
    def test_enrich_account(self):
        """Test account enrichment."""
        detail = {
            "accountId": "123456789012",
            "eventType": "ConsoleLogin"
        }
        
        enrichment = enrich_account(detail)
        
        assert enrichment["accountId"] == "123456789012"
        assert "accountName" in enrichment
    
    def test_unusual_location_detection(self):
        """Test detection of unusual location changes."""
        detail = {
            "country": "NG",
            "previousLoginCountry": "US",
            "timeSinceLastLogin": "1h"  # 1 hour apart
        }
        
        result = is_unusual_location(detail)
        
        assert result is True
    
    def test_usual_location_same_country(self):
        """Test that same country is not unusual."""
        detail = {
            "country": "US",
            "previousLoginCountry": "US"
        }
        
        result = is_unusual_location(detail)
        
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
