from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


class Agency(BaseModel):
    """Model for agency data"""
    agency_id: str
    agency_name: str
    created_at: Optional[datetime] = None
    status: Optional[str] = None
    location: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None
    nationalities: Optional[str] = None
    contract_duration: Optional[str] = None
    health_insurance: Optional[str] = None
    liability_insurance: Optional[str] = None
    accident_insurance: Optional[str] = None
    hours_per_week: Optional[str] = None
    night_care: Optional[str] = None
    ger_minimum_wage: Optional[str] = None
    is_active_recently: Optional[bool] = None

    class Config:
        allow_population_by_field_name = True
        orm_mode = True


class KPIData(BaseModel):
    """Model for KPI data of an agency"""
    agency_id: str
    total_jobs_viewed: Optional[int] = 0
    total_jobs_reserved: Optional[int] = 0
    total_jobs_fulfilled: Optional[int] = 0 
    total_jobs_cancelled: Optional[int] = 0
    total_jobs_pending: Optional[int] = 0
    total_caregivers_assigned: Optional[int] = 0
    total_caregivers_started: Optional[int] = 0
    total_ended_early: Optional[int] = 0
    total_completed: Optional[int] = 0
    reservation_rate: Optional[float] = 0.0
    fulfillment_rate: Optional[float] = 0.0
    cancellation_rate: Optional[float] = 0.0
    start_rate: Optional[float] = 0.0
    completion_rate: Optional[float] = 0.0
    early_end_rate: Optional[float] = 0.0
    agency_name: Optional[str] = None


class ResponseTimeData(BaseModel):
    """Model for response time data of an agency"""
    agency_id: str
    avg_time_to_reservation: Optional[float] = 0.0
    avg_time_to_proposal: Optional[float] = 0.0
    avg_time_to_cancellation: Optional[float] = 0.0
    avg_time_before_start: Optional[float] = 0.0
    avg_time_to_any_cancellation: Optional[float] = 0.0
    agency_name: Optional[str] = None


class ProfileQualityData(BaseModel):
    """Model for profile quality data of an agency"""
    agency_id: str
    total_caregivers: Optional[int] = 0
    experience_violations: Optional[int] = 0
    language_violations: Optional[int] = 0
    smoker_violations: Optional[int] = 0
    age_violations: Optional[int] = 0
    license_violations: Optional[int] = 0
    experience_violation_rate: Optional[float] = 0.0
    language_violation_rate: Optional[float] = 0.0
    smoker_violation_rate: Optional[float] = 0.0
    age_violation_rate: Optional[float] = 0.0
    license_violation_rate: Optional[float] = 0.0
    agency_name: Optional[str] = None


class TimeFilter(BaseModel):
    """Model for time period filter"""
    time_period: str = Field(
        "last_quarter", 
        description="Time period for data filtering", 
        pattern="^(last_quarter|last_month|last_year|all_time)$"
    )


class AgencyRequest(BaseModel):
    """Model for agency request with optional time period"""
    agency_id: str
    time_period: Optional[str] = "last_quarter"


class LLMAnalysisResult(BaseModel):
    """Model for LLM analysis results"""
    agency_id: str
    analysis_type: str
    reason_categories: Dict[str, int]
    total_analyzed: int
    agency_name: Optional[str] = None


class AgencyComparison(BaseModel):
    """Model for agency comparison data"""
    selected_agency: KPIData
    all_agencies: List[KPIData]
    industry_average: KPIData


class ResponseTimeComparison(BaseModel):
    """Model for response time comparison data"""
    selected_agency: ResponseTimeData
    all_agencies: List[ResponseTimeData]
    industry_average: ResponseTimeData


class ProfileQualityComparison(BaseModel):
    """Model for profile quality comparison data"""
    selected_agency: ProfileQualityData
    all_agencies: List[ProfileQualityData]
    industry_average: ProfileQualityData


class StrengthWeaknessAnalysis(BaseModel):
    """Model for strength/weakness analysis"""
    agency_id: str
    agency_name: Optional[str] = None
    strengths: List[Dict[str, Any]]
    weaknesses: List[Dict[str, Any]]
    neutral: List[Dict[str, Any]]
    overall_score: float 