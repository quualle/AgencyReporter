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


# CV Quality Analysis Models
class CareStayInfo(BaseModel):
    """Model for care stay information"""
    care_stay_id: str
    agency_id: str
    agency_name: str
    customer_id: str
    start_date: Optional[str]
    end_date: Optional[str]
    status: str
    cancellation_reason: Optional[str]
    cancelled_before_arrival: bool
    duration_days: Optional[int]
    # Caregiver Instance Daten
    caregiver_instance_id: str
    caregiver_id: str
    caregiver_birthday: Optional[str]
    caregiver_experience: Optional[str]
    caregiver_experience_germany: Optional[str]
    caregiver_description: Optional[str]
    caregiver_phone: Optional[str]
    caregiver_external_id: Optional[str]
    caregiver_german_score: Optional[str]  # Deutschnote (1-5 oder 1-6 Skala)
    caregiver_german_level: Optional[str]  # Interpretierte Deutschkenntnisse
    # Caregiver Basis Daten
    caregiver_first_name: Optional[str]
    caregiver_last_name: Optional[str]
    caregiver_full_name: Optional[str]
    caregiver_gender: Optional[str]
    caregiver_salutation: Optional[str]
    # Household/Customer Daten
    household_id: Optional[str]
    lead_id: Optional[str]
    household_designation: Optional[str]
    is_customer: Optional[str]
    household_notes: Optional[str]
    # Lead Contact Info (Ansprechpartner/Entscheider)
    lead_first_name: Optional[str]
    lead_last_name: Optional[str]
    lead_full_name: Optional[str]
    lead_email: Optional[str]
    lead_phone: Optional[str]
    lead_sales_partner: Optional[str]  # Vertriebspartner
    # Care Location (wo die Pflege stattfindet)
    care_location_street: Optional[str]
    care_location_zip: Optional[str]
    care_location_city: Optional[str]
    care_location_full: Optional[str]
    # Care Receiver Info (Pflegebedürftiger)
    care_receiver_first_name: Optional[str]
    care_receiver_last_name: Optional[str]
    care_receiver_full_name: Optional[str]
    care_receiver_care_level: Optional[str]


class CVAnalysisRequest(BaseModel):
    """Model for CV analysis request"""
    care_stay_id: str
    cv_content: str


class CVCategory(BaseModel):
    """Model for individual CV category analysis"""
    category_name: str
    cv_claim: str
    fulfillment_score: float  # 1-5 scale
    confidence: float  # 0-1 confidence in the assessment
    evidence: List[str]  # Quotes from communications
    discrepancy_detected: bool


class CVAnalysisResult(BaseModel):
    """Model for complete CV analysis result"""
    care_stay_id: str
    analysis_date: datetime
    categories: Dict[str, CVCategory]
    fulfillment_scores: Dict[str, float]
    discrepancies: List[Dict[str, Any]]
    overall_score: float
    details: Dict[str, Any]
    recommendations: List[str] 