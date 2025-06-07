"""
Database models for persistent cache storage.
Replaces in-memory cache with SQLite-based persistent storage.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Index, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json
import hashlib

Base = declarative_base()


class CachedData(Base):
    """
    Stores cached API responses with metadata for cache management.
    Replaces the in-memory cache system.
    """
    __tablename__ = "cached_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cache_key = Column(String(500), unique=True, nullable=False, index=True)
    endpoint = Column(String(200), nullable=False, index=True)
    agency_id = Column(String(100), nullable=True, index=True)
    time_period = Column(String(50), nullable=True, index=True)
    parameters = Column(Text, nullable=True)  # JSON string for additional parameters
    data = Column(Text, nullable=False)  # JSON string of API response
    created_at = Column(DateTime, default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=True, index=True)
    is_preloaded = Column(Boolean, default=False, nullable=False)
    data_hash = Column(String(64), nullable=True)  # SHA256 hash for data integrity
    
    # Composite indexes for common query patterns
    __table_args__ = (
        Index('idx_agency_period', 'agency_id', 'time_period'),
        Index('idx_endpoint_agency', 'endpoint', 'agency_id'),
        Index('idx_expires_preloaded', 'expires_at', 'is_preloaded'),
    )

    def set_data(self, data_dict: Dict[Any, Any]) -> None:
        """Set data and compute hash for integrity checking."""
        def json_serializer(obj):
            """Custom JSON serializer for datetime and other objects."""
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()
            return str(obj)
        
        json_data = json.dumps(data_dict, sort_keys=True, default=json_serializer)
        self.data = json_data
        self.data_hash = hashlib.sha256(json_data.encode()).hexdigest()

    def get_data(self) -> Dict[Any, Any]:
        """Get data as dictionary."""
        return json.loads(self.data)

    def set_parameters(self, params: Dict[str, Any]) -> None:
        """Set parameters as JSON string."""
        self.parameters = json.dumps(params, sort_keys=True) if params else None

    def get_parameters(self) -> Optional[Dict[str, Any]]:
        """Get parameters as dictionary."""
        return json.loads(self.parameters) if self.parameters else None

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    def set_expiry(self, hours: int) -> None:
        """Set expiry time from now."""
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)

    def __repr__(self):
        return f"<CachedData(cache_key='{self.cache_key}', endpoint='{self.endpoint}', agency_id='{self.agency_id}')>"


class PreloadSession(Base):
    """
    Tracks preload sessions to prevent duplicate loading and provide progress updates.
    """
    __tablename__ = "preload_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agency_id = Column(String(100), nullable=False, index=True)
    session_key = Column(String(200), unique=True, nullable=False, index=True)
    started_at = Column(DateTime, default=func.now(), nullable=False)
    completed_at = Column(DateTime, nullable=True)
    total_requests = Column(Integer, default=0, nullable=False)
    successful_requests = Column(Integer, default=0, nullable=False)
    failed_requests = Column(Integer, default=0, nullable=False)
    status = Column(String(50), default='running', nullable=False)  # running, completed, failed, cancelled
    error_message = Column(Text, nullable=True)
    
    # Composite index for session queries
    __table_args__ = (
        Index('idx_agency_session', 'agency_id', 'session_key'),
        Index('idx_status_started', 'status', 'started_at'),
    )

    def mark_completed(self) -> None:
        """Mark session as completed."""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()

    def mark_failed(self, error_msg: str) -> None:
        """Mark session as failed with error message."""
        self.status = 'failed'
        self.completed_at = datetime.utcnow()
        self.error_message = error_msg

    def get_success_rate(self) -> float:
        """Calculate success rate of the session."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100

    def is_active(self) -> bool:
        """Check if session is still running."""
        return self.status == 'running'

    def get_duration_minutes(self) -> Optional[float]:
        """Get session duration in minutes."""
        end_time = self.completed_at or datetime.utcnow()
        duration = end_time - self.started_at
        return duration.total_seconds() / 60

    def __repr__(self):
        return f"<PreloadSession(agency_id='{self.agency_id}', status='{self.status}', success_rate={self.get_success_rate():.1f}%)>"


class DataFreshness(Base):
    """
    Tracks data freshness to determine when data should be refreshed.
    Enables intelligent caching decisions.
    """
    __tablename__ = "data_freshness"

    id = Column(Integer, primary_key=True, autoincrement=True)
    data_type = Column(String(100), nullable=False, index=True)  # quotas, reaction_times, problematic_stays
    agency_id = Column(String(100), nullable=True, index=True)
    time_period = Column(String(50), nullable=True, index=True)
    last_updated = Column(DateTime, default=func.now(), nullable=False)
    source_query_executed_at = Column(DateTime, nullable=True)  # When BigQuery was last executed
    is_fresh = Column(Boolean, default=True, nullable=False, index=True)
    freshness_duration_hours = Column(Integer, default=24, nullable=False)  # How long data stays fresh
    
    # Ensure uniqueness per data type/agency/period combination
    __table_args__ = (
        UniqueConstraint('data_type', 'agency_id', 'time_period', name='unique_data_freshness'),
        Index('idx_freshness_check', 'data_type', 'agency_id', 'time_period', 'is_fresh'),
    )

    def update_freshness(self) -> None:
        """Update the last_updated timestamp and mark as fresh."""
        self.last_updated = datetime.utcnow()
        self.is_fresh = True

    def mark_stale(self) -> None:
        """Mark data as stale/not fresh."""
        self.is_fresh = False

    def is_data_fresh(self) -> bool:
        """
        Check if data is still considered fresh based on freshness duration.
        """
        if not self.is_fresh:
            return False
        
        age_hours = (datetime.utcnow() - self.last_updated).total_seconds() / 3600
        return age_hours < self.freshness_duration_hours

    def get_age_hours(self) -> float:
        """Get the age of the data in hours."""
        return (datetime.utcnow() - self.last_updated).total_seconds() / 3600

    def time_until_stale_hours(self) -> float:
        """Get hours until data becomes stale."""
        age = self.get_age_hours()
        return max(0, self.freshness_duration_hours - age)

    @classmethod
    def get_freshness_duration(cls, data_type: str, time_period: str) -> int:
        """
        Get appropriate freshness duration based on data type and time period.
        
        Rules:
        - quotas: 24h for historical periods, 4h for current periods
        - reaction_times: 12h for historical, 2h for current
        - problematic_stays: 24h for historical, 6h for current
        - all_time: 7 days (weekly refresh)
        """
        freshness_rules = {
            "quotas": {
                "last_quarter": 24, "last_year": 48, "last_month": 24, "all_time": 168,
                "current_quarter": 4, "current_year": 6, "current_month": 2
            },
            "reaction_times": {
                "last_quarter": 12, "last_year": 24, "last_month": 12, "all_time": 72,
                "current_quarter": 2, "current_year": 3, "current_month": 1
            },
            "problematic_stays": {
                "last_quarter": 24, "last_year": 48, "last_month": 24, "all_time": 168,
                "current_quarter": 6, "current_year": 8, "current_month": 4
            }
        }
        
        return freshness_rules.get(data_type, {}).get(time_period, 24)  # Default: 24 hours

    def __repr__(self):
        return f"<DataFreshness(data_type='{self.data_type}', agency_id='{self.agency_id}', is_fresh={self.is_fresh}, age={self.get_age_hours():.1f}h)>"


class CVAnalysisResult(Base):
    """
    Stores CV quality analysis results for care stays.
    """
    __tablename__ = "cv_analysis_results"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    care_stay_id = Column(String(200), nullable=False, index=True)
    agency_id = Column(String(100), nullable=True, index=True)
    analysis_date = Column(DateTime, default=func.now(), nullable=False)
    cv_categories = Column(Text, nullable=True)  # JSON string with category details
    fulfillment_scores = Column(Text, nullable=True)  # JSON string with category -> score mapping
    discrepancies = Column(Text, nullable=True)  # JSON string with list of detected discrepancies
    overall_score = Column(Integer, nullable=True)  # Overall score as float stored as integer (multiply by 10)
    analysis_details = Column(Text, nullable=True)  # JSON string with additional analysis metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Composite indexes for common query patterns
    __table_args__ = (
        Index('idx_cv_care_stay', 'care_stay_id'),
        Index('idx_cv_agency', 'agency_id'),
        Index('idx_cv_analysis_date', 'analysis_date'),
        Index('idx_cv_agency_score', 'agency_id', 'overall_score'),
    )
    
    def set_categories(self, categories: Dict[str, Any]) -> None:
        """Set categories as JSON string."""
        self.cv_categories = json.dumps(categories, sort_keys=True)
    
    def get_categories(self) -> Dict[str, Any]:
        """Get categories as dictionary."""
        return json.loads(self.cv_categories) if self.cv_categories else {}
    
    def set_fulfillment_scores(self, scores: Dict[str, float]) -> None:
        """Set fulfillment scores as JSON string."""
        self.fulfillment_scores = json.dumps(scores, sort_keys=True)
    
    def get_fulfillment_scores(self) -> Dict[str, float]:
        """Get fulfillment scores as dictionary."""
        return json.loads(self.fulfillment_scores) if self.fulfillment_scores else {}
    
    def set_discrepancies(self, discrepancies: list) -> None:
        """Set discrepancies as JSON string."""
        self.discrepancies = json.dumps(discrepancies, sort_keys=True)
    
    def get_discrepancies(self) -> list:
        """Get discrepancies as list."""
        return json.loads(self.discrepancies) if self.discrepancies else []
    
    def set_analysis_details(self, details: Dict[str, Any]) -> None:
        """Set analysis details as JSON string."""
        self.analysis_details = json.dumps(details, sort_keys=True)
    
    def get_analysis_details(self) -> Dict[str, Any]:
        """Get analysis details as dictionary."""
        return json.loads(self.analysis_details) if self.analysis_details else {}
    
    def set_overall_score(self, score: float) -> None:
        """Set overall score (store as integer by multiplying by 10)."""
        self.overall_score = int(score * 10)
    
    def get_overall_score(self) -> float:
        """Get overall score as float."""
        return self.overall_score / 10.0 if self.overall_score is not None else 5.0
    
    def __repr__(self):
        return f"<CVAnalysisResult(care_stay_id='{self.care_stay_id}', agency_id='{self.agency_id}', overall_score={self.get_overall_score()})>"