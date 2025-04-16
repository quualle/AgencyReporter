from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from ..utils.bigquery_connection import BigQueryConnection
from ..utils.openai_integration import OpenAIIntegration
from ..models import LLMAnalysisResult, TimeFilter, AgencyRequest, StrengthWeaknessAnalysis
from ..dependencies import get_settings
import openai

router = APIRouter()

@router.get("/{agency_id}/cancellations", response_model=LLMAnalysisResult)
async def get_cancellation_analysis(
    agency_id: str, 
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get LLM analysis of cancellation reasons for a specific agency
    """
    try:
        # Connect to BigQuery
        bq = BigQueryConnection()
        
        # Get cancellation texts from BigQuery
        # This would be actual emails, tickets, notes, etc. related to cancellations
        cancellation_texts = bq.get_cancellation_texts(agency_id, time_period)
        
        # If no texts are found, return mock data
        if not cancellation_texts or len(cancellation_texts) == 0:
            # Return mock data for development/demo purposes
            mock_result = {
                "agency_id": agency_id,
                "analysis_type": "cancellations",
                "reason_categories": {
                    "caregiver_unavailable": 5,
                    "customer_dissatisfied": 3,
                    "health_issues": 7,
                    "communication_problems": 4,
                    "administrative_issues": 2
                },
                "total_analyzed": 21
            }
            return mock_result
        
        # Initialize OpenAI integration
        openai_integration = OpenAIIntegration()
        
        # Analyze cancellation texts
        analysis_result = openai_integration.analyze_cancellations(cancellation_texts)
        
        # Create result object
        result = {
            "agency_id": agency_id,
            "analysis_type": "cancellations",
            "reason_categories": analysis_result["reason_categories"],
            "total_analyzed": analysis_result["total_analyzed"]
        }
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to perform cancellation analysis: {str(e)}")

@router.get("/{agency_id}/violations", response_model=LLMAnalysisResult)
async def get_violations_analysis(
    agency_id: str, 
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get LLM analysis of profile violations for a specific agency
    """
    try:
        # Connect to BigQuery
        bq = BigQueryConnection()
        
        # Get violation texts from BigQuery
        # This would be actual emails, tickets, notes, etc. related to profile violations
        violation_texts = bq.get_violation_texts(agency_id, time_period)
        
        # If no texts are found, return mock data
        if not violation_texts or len(violation_texts) == 0:
            # Return mock data for development/demo purposes
            mock_result = {
                "agency_id": agency_id,
                "analysis_type": "violations",
                "reason_categories": {
                    "experience_misrepresentation": 8,
                    "language_skill_exaggeration": 12,
                    "smoking_status_incorrect": 3,
                    "age_discrepancy": 2,
                    "license_issues": 5
                },
                "total_analyzed": 30
            }
            return mock_result
        
        # Initialize OpenAI integration
        openai_integration = OpenAIIntegration()
        
        # Analyze violation texts
        analysis_result = openai_integration.analyze_violations(violation_texts)
        
        # Create result object
        result = {
            "agency_id": agency_id,
            "analysis_type": "violations",
            "reason_categories": analysis_result["reason_categories"],
            "total_analyzed": analysis_result["total_analyzed"]
        }
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to perform violations analysis: {str(e)}")

@router.get("/{agency_id}/summary", response_model=Dict[str, str])
async def get_agency_summary(
    agency_id: str, 
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get an AI-generated summary of agency performance
    """
    try:
        # Connect to BigQuery
        bq = BigQueryConnection()
        
        # Get agency data
        kpi_data = bq.get_kpis_by_agency(agency_id, time_period)
        response_time_data = bq.get_response_times_by_agency(agency_id, time_period)
        profile_quality_data = bq.get_profile_quality_by_agency(agency_id, time_period)
        
        # Get strength/weakness analysis
        strength_weakness_data = _analyze_strength_weakness(
            agency_id,
            kpi_data,
            response_time_data,
            profile_quality_data,
            bq.get_all_agencies_kpis(time_period)
        )
        
        # Combine data for summary
        agency_data = {
            "agency_id": agency_id,
            "agency_name": kpi_data.get("agency_name", "Unknown Agency"),
            "kpis": kpi_data,
            "response_times": response_time_data,
            "profile_quality": profile_quality_data,
            "strength_weakness": {
                "strengths_count": len(strength_weakness_data.get("strengths", [])),
                "weaknesses_count": len(strength_weakness_data.get("weaknesses", [])),
                "overall_score": strength_weakness_data.get("overall_score", 0)
            }
        }
        
        # Initialize OpenAI integration
        openai_integration = OpenAIIntegration()
        
        # Generate summary
        summary = openai_integration.summarize_agency_performance(agency_data)
        
        return {"agency_id": agency_id, "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate agency summary: {str(e)}")

@router.get("/{agency_id}/strength-weakness", response_model=StrengthWeaknessAnalysis)
async def get_strength_weakness_analysis(
    agency_id: str, 
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get strength and weakness analysis for a specific agency
    """
    try:
        bq = BigQueryConnection()
        
        # Get KPIs
        kpi_data = bq.get_kpis_by_agency(agency_id, time_period)
        
        # Get response times
        response_time_data = bq.get_response_times_by_agency(agency_id, time_period)
        
        # Get profile quality
        profile_quality_data = bq.get_profile_quality_by_agency(agency_id, time_period)
        
        # Get all agencies data for comparison
        all_agencies_kpis = bq.get_all_agencies_kpis(time_period)
        
        # Perform strength/weakness analysis
        analysis = _analyze_strength_weakness(
            agency_id,
            kpi_data,
            response_time_data,
            profile_quality_data,
            all_agencies_kpis
        )
        
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to perform strength/weakness analysis: {str(e)}")

def _analyze_strength_weakness(
    agency_id: str,
    kpi_data: Dict[str, Any],
    response_time_data: Dict[str, Any],
    profile_quality_data: Dict[str, Any],
    all_agencies_kpis: List[Dict[str, Any]]
) -> StrengthWeaknessAnalysis:
    """
    Analyze strengths and weaknesses of an agency based on its metrics
    """
    # Get agency name
    agency_name = kpi_data.get("agency_name", "Unknown Agency")
    
    # Calculate industry averages for KPIs
    industry_avg_kpis = {}
    if all_agencies_kpis:
        for key in ["reservation_rate", "fulfillment_rate", "cancellation_rate", "start_rate", "completion_rate", "early_end_rate"]:
            values = [agency.get(key, 0) for agency in all_agencies_kpis if agency.get(key) is not None]
            if values:
                industry_avg_kpis[key] = sum(values) / len(values)
            else:
                industry_avg_kpis[key] = 0
    
    # Initialize strengths, weaknesses, and neutral lists
    strengths = []
    weaknesses = []
    neutral = []
    
    # Analyze KPI data
    if kpi_data:
        # Reservation rate
        _compare_metric(
            strengths, weaknesses, neutral,
            kpi_data.get("reservation_rate"),
            industry_avg_kpis.get("reservation_rate", 0),
            "reservation_rate",
            "Reservierungsrate",
            higher_is_better=True,
            threshold=0.1  # 10% threshold
        )
        
        # Fulfillment rate
        _compare_metric(
            strengths, weaknesses, neutral,
            kpi_data.get("fulfillment_rate"),
            industry_avg_kpis.get("fulfillment_rate", 0),
            "fulfillment_rate",
            "Erfüllungsrate",
            higher_is_better=True,
            threshold=0.1
        )
        
        # Cancellation rate
        _compare_metric(
            strengths, weaknesses, neutral,
            kpi_data.get("cancellation_rate"),
            industry_avg_kpis.get("cancellation_rate", 0),
            "cancellation_rate",
            "Abbruchrate",
            higher_is_better=False,
            threshold=0.1
        )
        
        # Start rate
        _compare_metric(
            strengths, weaknesses, neutral,
            kpi_data.get("start_rate"),
            industry_avg_kpis.get("start_rate", 0),
            "start_rate",
            "Antrittsrate",
            higher_is_better=True,
            threshold=0.1
        )
        
        # Completion rate
        _compare_metric(
            strengths, weaknesses, neutral,
            kpi_data.get("completion_rate"),
            industry_avg_kpis.get("completion_rate", 0),
            "completion_rate",
            "Abschlussrate",
            higher_is_better=True,
            threshold=0.1
        )
        
        # Early end rate
        _compare_metric(
            strengths, weaknesses, neutral,
            kpi_data.get("early_end_rate"),
            industry_avg_kpis.get("early_end_rate", 0),
            "early_end_rate",
            "Frühzeitige Beendigungsrate",
            higher_is_better=False,
            threshold=0.1
        )
    
    # Analyze response time data
    if response_time_data:
        # Time to reservation
        _compare_metric(
            strengths, weaknesses, neutral,
            response_time_data.get("avg_time_to_reservation"),
            24,  # Benchmark value (24 hours)
            "avg_time_to_reservation",
            "Zeit bis zur Reservierung",
            higher_is_better=False,
            threshold=6  # 6 hours threshold
        )
        
        # Time to proposal
        _compare_metric(
            strengths, weaknesses, neutral,
            response_time_data.get("avg_time_to_proposal"),
            48,  # Benchmark value (48 hours)
            "avg_time_to_proposal",
            "Zeit bis zum Personalvorschlag",
            higher_is_better=False,
            threshold=12  # 12 hours threshold
        )
    
    # Analyze profile quality data
    if profile_quality_data:
        # Experience violation rate
        _compare_metric(
            strengths, weaknesses, neutral,
            profile_quality_data.get("experience_violation_rate"),
            0.1,  # Benchmark value (10%)
            "experience_violation_rate",
            "Erfahrungs-Regelverstöße",
            higher_is_better=False,
            threshold=0.05  # 5% threshold
        )
        
        # Language violation rate
        _compare_metric(
            strengths, weaknesses, neutral,
            profile_quality_data.get("language_violation_rate"),
            0.1,  # Benchmark value (10%)
            "language_violation_rate",
            "Sprachkenntnis-Regelverstöße",
            higher_is_better=False,
            threshold=0.05  # 5% threshold
        )
    
    # Calculate overall score (simple average of normalized scores)
    scores = []
    for item in strengths:
        scores.append(item.get("normalized_score", 0))
    for item in weaknesses:
        scores.append(item.get("normalized_score", 0))
    for item in neutral:
        scores.append(item.get("normalized_score", 0))
    
    overall_score = sum(scores) / len(scores) if scores else 0
    
    # Create and return the analysis
    return {
        "agency_id": agency_id,
        "agency_name": agency_name,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "neutral": neutral,
        "overall_score": overall_score
    }

def _compare_metric(
    strengths: List[Dict[str, Any]],
    weaknesses: List[Dict[str, Any]],
    neutral: List[Dict[str, Any]],
    value: Any,
    benchmark: Any,
    metric_key: str,
    metric_name: str,
    higher_is_better: bool = True,
    threshold: float = 0.1
):
    """
    Compare a metric with a benchmark and categorize it as strength, weakness, or neutral
    """
    # Skip if value is None
    if value is None:
        return
    
    try:
        # Convert to float
        value = float(value)
        benchmark = float(benchmark)
        
        # Calculate difference
        diff = value - benchmark
        
        # Determine if it's a strength, weakness, or neutral
        if higher_is_better:
            if diff > threshold:
                category = "strength"
                category_name = "Stärke"
            elif diff < -threshold:
                category = "weakness"
                category_name = "Schwäche"
            else:
                category = "neutral"
                category_name = "Neutral"
        else:
            if diff < -threshold:
                category = "strength"
                category_name = "Stärke"
            elif diff > threshold:
                category = "weakness"
                category_name = "Schwäche"
            else:
                category = "neutral"
                category_name = "Neutral"
        
        # Calculate normalized score (0-1 scale, 1 is best)
        if higher_is_better:
            # For metrics where higher is better
            normalized_score = min(1.0, max(0.0, (value / (benchmark * 2))))
        else:
            # For metrics where lower is better
            normalized_score = min(1.0, max(0.0, (benchmark / (value + 0.01))))
        
        # Format percentage values
        if metric_key.endswith("_rate"):
            value_formatted = f"{value * 100:.1f}%"
            benchmark_formatted = f"{benchmark * 100:.1f}%"
        else:
            value_formatted = f"{value:.1f}"
            benchmark_formatted = f"{benchmark:.1f}"
        
        # Create result object
        result = {
            "metric_key": metric_key,
            "metric_name": metric_name,
            "value": value,
            "value_formatted": value_formatted,
            "benchmark": benchmark,
            "benchmark_formatted": benchmark_formatted,
            "difference": diff,
            "category": category,
            "category_name": category_name,
            "normalized_score": normalized_score
        }
        
        # Add to appropriate list
        if category == "strength":
            strengths.append(result)
        elif category == "weakness":
            weaknesses.append(result)
        else:
            neutral.append(result)
    
    except (ValueError, TypeError):
        # Skip if value or benchmark cannot be converted to float
        pass 