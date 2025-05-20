from fastapi.testclient import TestClient
import pytest
from app.main import app
from unittest.mock import patch, MagicMock

# Create test client
client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "API is running"}

def test_root():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

@patch("app.routes.agencies.BigQueryConnection")
def test_get_agencies(mock_bigquery):
    """Test the get agencies endpoint"""
    # Mock the BigQuery connection
    mock_instance = MagicMock()
    mock_instance.get_agencies.return_value = [
        {
            "agency_id": "agency1",
            "agency_name": "Test Agency 1",
            "status": "active"
        },
        {
            "agency_id": "agency2",
            "agency_name": "Test Agency 2",
            "status": "active"
        }
    ]
    mock_bigquery.return_value = mock_instance
    
    # Call the endpoint
    response = client.get("/api/agencies/")
    
    # Check the response
    assert response.status_code == 200
    agencies = response.json()
    assert len(agencies) == 2
    assert agencies[0]["agency_id"] == "agency1"
    assert agencies[1]["agency_name"] == "Test Agency 2"

@patch("app.routes.kpis.BigQueryConnection")
def test_get_agency_kpis(mock_bigquery):
    """Test the get agency KPIs endpoint"""
    # Mock the BigQuery connection
    mock_instance = MagicMock()
    mock_instance.get_kpis_by_agency.return_value = {
        "agency_id": "agency1",
        "total_jobs_viewed": 100,
        "total_jobs_reserved": 50,
        "reservation_rate": 0.5
    }
    mock_bigquery.return_value = mock_instance
    
    # Call the endpoint
    response = client.get("/api/kpis/agency1?time_period=last_quarter")
    
    # Check the response
    assert response.status_code == 200
    kpis = response.json()
    assert kpis["agency_id"] == "agency1"
    assert kpis["total_jobs_viewed"] == 100
    assert kpis["reservation_rate"] == 0.5

@patch("app.routes.response_times.BigQueryConnection")
def test_get_agency_response_times(mock_bigquery):
    """Test the get agency response times endpoint"""
    # Mock the BigQuery connection
    mock_instance = MagicMock()
    mock_instance.get_response_times_by_agency.return_value = {
        "agency_id": "agency1",
        "avg_time_to_reservation": 12.5,
        "avg_time_to_proposal": 36.2
    }
    mock_bigquery.return_value = mock_instance
    
    # Call the endpoint
    response = client.get("/api/response-times/agency1?time_period=last_quarter")
    
    # Check the response
    assert response.status_code == 200
    times = response.json()
    assert times["agency_id"] == "agency1"
    assert times["avg_time_to_reservation"] == 12.5
    assert times["avg_time_to_proposal"] == 36.2

@patch("app.routes.llm_analysis.BigQueryConnection")
def test_get_strength_weakness_analysis(mock_bigquery):
    """Test the strength/weakness analysis endpoint"""
    # Mock the BigQuery connection
    mock_instance = MagicMock()
    mock_instance.get_kpis_by_agency.return_value = {
        "agency_id": "agency1",
        "agency_name": "Test Agency",
        "reservation_rate": 0.8,
        "cancellation_rate": 0.05
    }
    mock_instance.get_response_times_by_agency.return_value = {
        "avg_time_to_reservation": 10.0
    }
    mock_instance.get_profile_quality_by_agency.return_value = {
        "experience_violation_rate": 0.02
    }
    mock_instance.get_all_agencies_kpis.return_value = [
        {
            "agency_id": "agency1",
            "reservation_rate": 0.8,
            "cancellation_rate": 0.05
        },
        {
            "agency_id": "agency2",
            "reservation_rate": 0.6,
            "cancellation_rate": 0.1
        }
    ]
    mock_bigquery.return_value = mock_instance
    
    # Call the endpoint
    response = client.get("/api/llm-analysis/agency1/strength-weakness?time_period=last_quarter")
    
    # Check the response
    assert response.status_code == 200
    analysis = response.json()
    assert analysis["agency_id"] == "agency1"
    assert "strengths" in analysis
    assert "weaknesses" in analysis
    assert "overall_score" in analysis 

@patch("app.routes.llm_analysis.BigQueryConnection")
@patch("app.routes.llm_analysis.OpenAIIntegration")
def test_get_cancellation_analysis(mock_openai, mock_bigquery):
    """Test the cancellation analysis endpoint"""
    # Mock the BigQuery connection
    mock_bq_instance = MagicMock()
    mock_bq_instance.get_cancellation_texts.return_value = [
        "Die Betreuungskraft hat eine bessere Stelle bekommen",
        "Der Kunde ist mit dem Profil unzufrieden"
    ]
    mock_bigquery.return_value = mock_bq_instance
    
    # Mock the OpenAI integration
    mock_openai_instance = MagicMock()
    mock_openai_instance.analyze_cancellations.return_value = {
        "reason_categories": {
            "better_offer": 1,
            "customer_dissatisfied": 1
        },
        "total_analyzed": 2
    }
    mock_openai.return_value = mock_openai_instance
    
    # Call the endpoint
    response = client.get("/api/llm-analysis/agency1/cancellations?time_period=last_quarter")
    
    # Check the response
    assert response.status_code == 200
    result = response.json()
    assert result["agency_id"] == "agency1"
    assert result["analysis_type"] == "cancellations"
    assert "reason_categories" in result
    assert result["total_analyzed"] == 2
    assert result["reason_categories"]["better_offer"] == 1
    assert result["reason_categories"]["customer_dissatisfied"] == 1

@patch("app.routes.llm_analysis.BigQueryConnection")
@patch("app.routes.llm_analysis.OpenAIIntegration")
def test_get_violations_analysis(mock_openai, mock_bigquery):
    """Test the violations analysis endpoint"""
    # Mock the BigQuery connection
    mock_bq_instance = MagicMock()
    mock_bq_instance.get_violation_texts.return_value = [
        "Die Deutschkenntnisse waren schlechter als angegeben",
        "Die Pflegekraft raucht, obwohl im Profil Nichtraucher angegeben"
    ]
    mock_bigquery.return_value = mock_bq_instance
    
    # Mock the OpenAI integration
    mock_openai_instance = MagicMock()
    mock_openai_instance.analyze_violations.return_value = {
        "reason_categories": {
            "language_skill_exaggeration": 1,
            "smoking_status_incorrect": 1
        },
        "total_analyzed": 2
    }
    mock_openai.return_value = mock_openai_instance
    
    # Call the endpoint
    response = client.get("/api/llm-analysis/agency1/violations?time_period=last_quarter")
    
    # Check the response
    assert response.status_code == 200
    result = response.json()
    assert result["agency_id"] == "agency1"
    assert result["analysis_type"] == "violations"
    assert "reason_categories" in result
    assert result["total_analyzed"] == 2
    assert result["reason_categories"]["language_skill_exaggeration"] == 1
    assert result["reason_categories"]["smoking_status_incorrect"] == 1

@patch("app.routes.llm_analysis.BigQueryConnection")
@patch("app.routes.llm_analysis.OpenAIIntegration")
def test_get_agency_summary(mock_openai, mock_bigquery):
    """Test the agency summary endpoint"""
    # Mock the BigQuery connection
    mock_bq_instance = MagicMock()
    mock_bq_instance.get_kpis_by_agency.return_value = {
        "agency_id": "agency1",
        "agency_name": "Test Agency",
        "reservation_rate": 0.8
    }
    mock_bq_instance.get_response_times_by_agency.return_value = {
        "avg_time_to_reservation": 10.0
    }
    mock_bq_instance.get_profile_quality_by_agency.return_value = {
        "experience_violation_rate": 0.02
    }
    mock_bq_instance.get_all_agencies_kpis.return_value = [
        {"agency_id": "agency1", "reservation_rate": 0.8},
        {"agency_id": "agency2", "reservation_rate": 0.6}
    ]
    mock_bigquery.return_value = mock_bq_instance
    
    # Mock the OpenAI integration
    mock_openai_instance = MagicMock()
    mock_openai_instance.summarize_agency_performance.return_value = "Die Agentur zeigt überdurchschnittliche Leistungen mit einer hohen Reservierungsrate."
    mock_openai.return_value = mock_openai_instance
    
    # Call the endpoint
    response = client.get("/api/llm-analysis/agency1/summary?time_period=last_quarter")
    
    # Check the response
    assert response.status_code == 200
    result = response.json()
    assert result["agency_id"] == "agency1"
    assert "summary" in result
    assert result["summary"] == "Die Agentur zeigt überdurchschnittliche Leistungen mit einer hohen Reservierungsrate." 