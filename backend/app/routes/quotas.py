from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Optional, Any
from ..utils.query_manager import QueryManager
from ..models import TimeFilter, AgencyRequest
from ..dependencies import get_settings
from ..services.database_cache_service import get_cache_service
from ..utils.cache_decorator import cache_endpoint

router = APIRouter()

@router.get("/postings")
@cache_endpoint(ttl_hours=24, key_params=['time_period'], cache_key_prefix="/quotas/postings")
async def get_posting_metrics(
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get metrics for all postings
    """
    try:
        query_manager = QueryManager()
        posting_metrics = query_manager.get_posting_metrics(time_period=time_period)
        return posting_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch posting metrics: {str(e)}")

@router.get("/{agency_id}/reservations")
@cache_endpoint(ttl_hours=24, key_params=['agency_id', 'time_period', 'start_date', 'end_date'], cache_key_prefix="/quotas/reservations")
async def get_agency_reservation_metrics(
    agency_id: str,
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$"),
    start_date: str = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(None, description="End date in YYYY-MM-DD format")
):
    """
    Get reservation metrics for a specific agency
    """
    try:
        query_manager = QueryManager()
        reservation_metrics = query_manager.get_agency_reservation_metrics(
            agency_id=agency_id,
            start_date=start_date,
            end_date=end_date,
            time_period=time_period
        )
        return reservation_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch reservation metrics: {str(e)}")

@router.get("/{agency_id}/fulfillment", deprecated=True)
@cache_endpoint(ttl_hours=24, key_params=['agency_id', 'time_period'], cache_key_prefix="/quotas/fulfillment")
async def get_fulfillment_rate(
    agency_id: str,
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    [DEPRECATED] Use /{agency_id}/reservation-fulfillment instead.
    Get fulfillment rate for a specific agency
    (Quote 2: Anzahl Reservierungen - Anzahl erfüllte Reservierungen)
    """
    try:
        query_manager = QueryManager()
        fulfillment_metrics = query_manager.get_reservation_fulfillment_rate(
            agency_id=agency_id,
            time_period=time_period
        )
        return fulfillment_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch fulfillment rate: {str(e)}")

@router.get("/{agency_id}/reservation-fulfillment")
@cache_endpoint(ttl_hours=24, key_params=['agency_id', 'time_period'], cache_key_prefix="/quotas/reservation-fulfillment")
async def get_reservation_fulfillment_rate(
    agency_id: str,
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get reservation fulfillment rate for a specific agency
    (Quote 2: Anzahl Reservierungen - Anzahl erfüllte Reservierungen)
    """
    try:
        query_manager = QueryManager()
        fulfillment_metrics = query_manager.get_fulfillment_rate(
            agency_id=agency_id,
            time_period=time_period
        )
        return fulfillment_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch reservation fulfillment rate: {str(e)}")

@router.get("/{agency_id}/withdrawal")
@cache_endpoint(ttl_hours=24, key_params=['agency_id', 'time_period'], cache_key_prefix="/quotas/withdrawal")
async def get_withdrawal_rate(
    agency_id: str,
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get withdrawal rate for a specific agency
    (Quote 3: Anzahl Reservierungen - Anzahl abgebrochene Reservierungen)
    """
    try:
        query_manager = QueryManager()
        withdrawal_metrics = query_manager.get_withdrawal_rate(
            agency_id=agency_id,
            time_period=time_period
        )
        return withdrawal_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch withdrawal rate: {str(e)}")

@router.get("/{agency_id}/pending")
@cache_endpoint(ttl_hours=24, key_params=['agency_id', 'time_period'], cache_key_prefix="/quotas/pending")
async def get_pending_rate(
    agency_id: str,
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get pending rate for a specific agency
    (Quote 4: Anzahl Reservierungen - Anzahl reservierungen, die weder zurückgezogen noch erfüllt wurden)
    """
    try:
        query_manager = QueryManager()
        pending_metrics = query_manager.get_pending_rate(
            agency_id=agency_id,
            time_period=time_period
        )
        return pending_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch pending rate: {str(e)}")

@router.get("/{agency_id}/arrival")
@cache_endpoint(ttl_hours=24, key_params=['agency_id', 'time_period'], cache_key_prefix="/quotas/arrival")
async def get_arrival_metrics(
    agency_id: str,
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get arrival metrics for a specific agency, differenziert nach Erst- und Folgeeinsätzen.
    Includes counts for different stages with the following flow:
    - All care stays (total)
    - First-time stays only (is_swap = false)
    - Follow-up stays only (is_swap = true)
    
    Stages follow this workflow:
    1. Reservation (reservation_fulfillment_count): Agentur reserviert einen freien Platz für ein Posting
    2. Personalvorschlag (pv_count): Care Stay wird erstellt mit Status "Neu" (jeder PV erzeugt einen Care Stay)
    3. "Vorgestellt": Status nach Vorstellung beim Kunden
    4. "Angenommen": Status nach Akzeptanz durch den Kunden (accepted_count)
    5. "Bestätigt": Status nach Bestätigung durch die Pflegekraft (confirmed_count)
    6. "Anreise": Tatsächliche Anreise, wenn nicht vorher abgebrochen (arrived_count)
    
    Notes:
    - For follow-up stays, reservation_fulfillment_count is always 0 as reservations are only possible for new postings
    - "PV count" counts all care stays (each care stay is a Personalvorschlag, regardless of status)
    - "Accepted" counts care stays that have reached status "Angenommen"
    - "Confirmed" counts care stays that have reached status "Bestätigt" (should be ≤ accepted)
    - "Arrived" counts care stays that have reached status "Bestätigt", have a valid arrival date, 
      and were NOT canceled before arrival (should be ≤ confirmed)
    
    Each category provides ratios between these stages, including the new pv_to_arrival_ratio.
    (Related to Quote 5)
    """
    try:
        query_manager = QueryManager()
        arrival_metrics = query_manager.get_arrival_metrics(
            agency_id=agency_id,
            time_period=time_period
        )
        return arrival_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch arrival metrics: {str(e)}")

@router.get("/{agency_id}/cancellation-before-arrival")
@cache_endpoint(ttl_hours=24, key_params=['agency_id', 'time_period'], cache_key_prefix="/quotas/cancellation-before-arrival")
async def get_cancellation_before_arrival_rate(
    agency_id: str,
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get cancellation before arrival rate for a specific agency
    (Quote 6: Anzahl gemachter Personalvorschläge - Anzahl VOR Einsatz abgebrochener Pflegeeinsätze)
    """
    try:
        query_manager = QueryManager()
        cancellation_metrics = query_manager.get_cancellation_before_arrival_rate(
            agency_id=agency_id,
            time_period=time_period
        )
        return cancellation_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch cancellation before arrival rate: {str(e)}")

@router.get("/all-agencies/completion")
@cache_endpoint(ttl_hours=24, key_params=['time_period'], cache_key_prefix="/quotas/all-agencies/completion")
async def get_all_agencies_completion_stats(
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get completion performance (completion rate and early termination rate) for all agencies.
    Shows conversion from started care stays to successfully completed ones.
    Returns: agency_id, agency_name, completion_rate, early_termination_rate, total_started, total_completed
    """
    try:
        query_manager = QueryManager()
        completion_stats = query_manager.get_all_agencies_completion_stats(time_period)
        return completion_stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch all agencies completion stats: {str(e)}")

@router.get("/{agency_id}/completion")
@cache_endpoint(ttl_hours=24, key_params=['agency_id', 'time_period'], cache_key_prefix="/quotas/completion")
async def get_completion_rate(
    agency_id: str,
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get completion rate for a specific agency
    (Quote 7: Pflegeeinsatz angetreten - Pflegeinsatz vollständig beendet)
    """
    try:
        query_manager = QueryManager()
        completion_metrics = query_manager.get_completion_rate(
            agency_id=agency_id,
            time_period=time_period
        )
        return completion_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch completion rate: {str(e)}")

@router.get("/{agency_id}/all")
@cache_endpoint(ttl_hours=24, key_params=['agency_id', 'time_period', 'start_date', 'end_date'], cache_key_prefix="/quotas/all")
async def get_all_quotas(
    agency_id: str,
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$"),
    start_date: str = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(None, description="End date in YYYY-MM-DD format")
):
    """
    Get all quota metrics for a specific agency
    """
    try:
        query_manager = QueryManager()
        all_quotas = query_manager.get_all_quotas(
            agency_id=agency_id,
            start_date=start_date,
            end_date=end_date,
            time_period=time_period
        )
        return all_quotas
    except Exception as e:
        # Check if it's a specific timestamp error and provide a more helpful message
        error_msg = str(e)
        if "Invalid timestamp" in error_msg and "252024" in error_msg:
            raise HTTPException(
                status_code=400, 
                detail=f"Data quality issue: Invalid timestamp found in database. This agency may have corrupted date data. Please contact support."
            )
        raise HTTPException(status_code=500, detail=f"Failed to fetch all quotas: {error_msg}")

@router.post("/custom")
async def get_custom_metrics(request: Dict[str, Any]):
    """
    Get custom metrics based on request parameters
    """
    try:
        query_manager = QueryManager()
        
        agency_id = request.get("agency_id")
        time_period = request.get("time_period", "last_quarter")
        metrics_type = request.get("metrics_type", "reservations")
        
        if not agency_id:
            raise HTTPException(status_code=400, detail="agency_id is required")
        
        if metrics_type == "reservations":
            metrics = query_manager.get_agency_reservation_metrics(
                agency_id=agency_id,
                time_period=time_period
            )
        elif metrics_type == "fulfillment":
            # Deprecated but still supported for backwards compatibility
            metrics = query_manager.get_reservation_fulfillment_rate(
                agency_id=agency_id,
                time_period=time_period
            )
        elif metrics_type == "reservation-fulfillment":
            metrics = query_manager.get_reservation_fulfillment_rate(
                agency_id=agency_id,
                time_period=time_period
            )
        elif metrics_type == "withdrawal":
            metrics = query_manager.get_withdrawal_rate(
                agency_id=agency_id,
                time_period=time_period
            )
        elif metrics_type == "pending":
            metrics = query_manager.get_pending_rate(
                agency_id=agency_id,
                time_period=time_period
            )
        elif metrics_type == "arrival":
            metrics = query_manager.get_arrival_metrics(
                agency_id=agency_id,
                time_period=time_period
            )
        elif metrics_type == "cancellation":
            metrics = query_manager.get_cancellation_before_arrival_rate(
                agency_id=agency_id,
                time_period=time_period
            )
        elif metrics_type == "completion":
            metrics = query_manager.get_completion_rate(
                agency_id=agency_id,
                time_period=time_period
            )
        elif metrics_type == "all":
            metrics = query_manager.get_all_quotas(
                agency_id=agency_id,
                time_period=time_period
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported metrics_type: {metrics_type}")
        
        return metrics
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch custom metrics: {str(e)}")

@router.get("/stats/overall/cancellation-before-arrival")
@cache_endpoint(ttl_hours=24, key_params=['start_date', 'end_date', 'time_period'], cache_key_prefix="/quotas/stats/overall/cancellation-before-arrival")
async def get_overall_cancellation_stats(
    start_date: Optional[str] = Query(None, description="Startdatum im Format YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="Enddatum im Format YYYY-MM-DD"),
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get overall average cancellation before arrival stats across all agencies.
    """
    try:
        query_manager = QueryManager()
        stats = query_manager.get_overall_cancellation_before_arrival_stats(start_date, end_date, time_period)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch overall cancellation before arrival stats: {str(e)}")

@router.get("/all-agencies/conversion")
@cache_endpoint(ttl_hours=24, key_params=['time_period'], cache_key_prefix="/quotas/all-agencies/conversion")
async def get_all_agencies_conversion_stats(
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get conversion performance (start rate and cancellation rate) for all agencies.
    Returns: agency_id, agency_name, start_rate, cancellation_rate, total_postings
    """
    try:
        query_manager = QueryManager()
        conversion_stats = query_manager.get_all_agencies_conversion_stats(time_period)
        return conversion_stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch all agencies conversion stats: {str(e)}")


@router.get("/{agency_id}/cancellations-before-arrival/details")
@cache_endpoint(ttl_hours=24, key_params=['agency_id', 'time_period'], cache_key_prefix="/quotas/cancellations-before-arrival/details")
async def get_cancellations_before_arrival_details(
    agency_id: str,
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get detailed list of individual cancellations before arrival for an agency.
    Returns individual care stay records that were cancelled before arrival.
    """
    try:
        
        query_manager = QueryManager()
        
        # Build the query - using tracks for cancellation info
        query = """
        WITH cancellation_details AS (
            SELECT
                cs._id as care_stay_id,
                cs.created_at,
                cs.arrival as planned_arrival,
                cs.rejection_reason as cancellation_reason,
                CONCAT(cr.first_name, ' ', cr.last_name) as customer_name,
                cr.location as customer_city,
                c.agency_id,
                a.name as agency_name,
                -- Extract cancellation date from tracks
                (SELECT TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at'))
                 FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
                 WHERE JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
                 ORDER BY JSON_EXTRACT_SCALAR(track, '$.created_at') DESC
                 LIMIT 1) as cancelled_at
            FROM
                `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
            JOIN
                `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
            JOIN
                `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies` a ON c.agency_id = a._id
            JOIN
                `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.households` h ON c.household_id = h._id
            LEFT JOIN
                `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_receivers` cr ON cr.household_id = h._id
            WHERE
                c.agency_id = @agency_id
                AND cs.created_at BETWEEN @start_date AND @end_date
                AND cs.stage = 'Abgebrochen'
                AND cs.arrival IS NOT NULL
                -- Confirmed before cancellation
                AND EXISTS (
                    SELECT 1
                    FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
                    WHERE JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Bestätigt'
                )
        )
        SELECT 
            *,
            DATE_DIFF(DATE(planned_arrival), DATE(cancelled_at), DAY) as days_before_arrival
        FROM cancellation_details
        WHERE cancelled_at IS NOT NULL
          AND cancelled_at < TIMESTAMP(planned_arrival)
        ORDER BY cancelled_at DESC
        """
        
        # Calculate date range
        start_date, end_date = query_manager._calculate_date_range(time_period)
        
        # Execute query
        from ..utils.bigquery_connection import BigQueryConnection
        connection = BigQueryConnection()
        results = connection.execute_query(query, {
            "agency_id": agency_id,
            "start_date": start_date,
            "end_date": end_date
        })
        
        # Format results
        details = []
        agency_name = "Unknown"
        
        for row in results:
            if not agency_name or agency_name == "Unknown":
                agency_name = row.get("agency_name", "Unknown")
                
            # Helper function to format dates
            def format_date(date_value):
                if not date_value:
                    return None
                if hasattr(date_value, 'isoformat'):
                    return date_value.isoformat()
                return str(date_value)
            
            detail = {
                "care_stay_id": row.get("care_stay_id"),
                "customer_name": row.get("customer_name"),
                "customer_city": row.get("customer_city"),
                "created_at": format_date(row.get("created_at")),
                "planned_arrival": format_date(row.get("planned_arrival")),
                "cancelled_at": format_date(row.get("cancelled_at")),
                "cancellation_reason": row.get("cancellation_reason"),
                "days_before_arrival": row.get("days_before_arrival")
            }
            details.append(detail)
        
        # Group by month
        from collections import defaultdict
        grouped_by_month = defaultdict(list)
        
        for detail in details:
            if detail["cancelled_at"]:
                month_key = detail["cancelled_at"][:7]  # YYYY-MM
                grouped_by_month[month_key].append(detail)
        
        # Convert to sorted list
        grouped_data = []
        for month in sorted(grouped_by_month.keys(), reverse=True):
            grouped_data.append({
                "month": month,
                "count": len(grouped_by_month[month]),
                "cancellations": grouped_by_month[month]
            })
        
        result = {
            "agency_id": agency_id,
            "agency_name": agency_name,
            "time_period": time_period,
            "total_count": len(details),
            "grouped_by_month": grouped_data
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch cancellation details: {str(e)}")


@router.get("/{agency_id}/early-terminations/details")
@cache_endpoint(ttl_hours=24, key_params=['agency_id', 'time_period'], cache_key_prefix="/quotas/early-terminations/details")
async def get_early_terminations_details(
    agency_id: str,
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$")
):
    """
    Get detailed list of individual early terminations after arrival for an agency.
    Returns individual care stay records that were terminated early (based on 33% rule).
    """
    try:
        
        query_manager = QueryManager()
        
        # Build the query - reusing logic from GET_ALL_AGENCIES_COMPLETION_STATS
        query = """
        WITH early_termination_details AS (
            WITH parsed AS (
                SELECT
                    cs._id as care_stay_id,
                    cs.arrival,
                    cs.departure,
                    cs.created_at,
                    cs.stage,
                    cs.rejection_reason as end_reason,
                    c.agency_id,
                    a.name as agency_name,
                    CONCAT(cr.first_name, ' ', cr.last_name) as customer_name,
                    cr.location as customer_city,
                    JSON_EXTRACT_ARRAY(cs.tracks) AS track_array,
                    -- Calculate actual stay duration
                    DATE_DIFF(DATE(cs.departure), DATE(cs.arrival), DAY) as actual_duration_days
                FROM
                    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
                JOIN
                    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
                JOIN
                    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies` a ON c.agency_id = a._id
                JOIN
                    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.households` h ON c.household_id = h._id
                LEFT JOIN
                    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_receivers` cr ON cr.household_id = h._id
                WHERE
                    c.agency_id = @agency_id
                    AND cs.created_at BETWEEN @start_date AND @end_date
                    AND cs.arrival IS NOT NULL
                    AND cs.arrival != ''
                    -- Must have reached "Bestätigt" status (started)
                    AND EXISTS (
                        SELECT 1
                        FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
                        WHERE JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Bestätigt'
                    )
                    -- Not cancelled before arrival
                    AND NOT (
                        cs.stage = 'Abgebrochen' AND 
                        EXISTS (
                            SELECT 1
                            FROM UNNEST(JSON_EXTRACT_ARRAY(cs.tracks)) AS track
                            WHERE 
                                JSON_EXTRACT_SCALAR(track, '$.differences.stage[1]') = 'Abgebrochen'
                                AND TIMESTAMP(JSON_EXTRACT_SCALAR(track, '$.created_at')) < TIMESTAMP(cs.arrival)
                        )
                    )
                    -- Must have a departure date
                    AND cs.departure IS NOT NULL
                    AND cs.departure != ''
                    -- Departure must be in the past (only completed stays)
                    AND TIMESTAMP(cs.departure) < CURRENT_TIMESTAMP()
            ),
            departure_changes AS (
                -- Extract departure changes to determine if early termination
                SELECT
                    p.care_stay_id,
                    p.agency_id,
                    p.customer_name,
                    p.customer_city,
                    p.arrival,
                    p.departure,
                    p.actual_duration_days,
                    p.end_reason,
                    -- Get the first departure change (original planned departure)
                    ARRAY_AGG(
                        STRUCT(
                            JSON_EXTRACT_SCALAR(track_item, '$.differences.departure[0]') AS original_departure,
                            JSON_EXTRACT_SCALAR(track_item, '$.differences.departure[1]') AS new_departure,
                            JSON_EXTRACT_SCALAR(track_item, '$.created_at') AS change_timestamp
                        )
                        ORDER BY JSON_EXTRACT_SCALAR(track_item, '$.created_at') ASC
                    )[OFFSET(0)] AS first_change
                FROM
                    parsed p,
                    UNNEST(p.track_array) AS track_item
                WHERE
                    JSON_EXTRACT_SCALAR(track_item, '$.differences.departure[0]') IS NOT NULL
                    AND SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', JSON_EXTRACT_SCALAR(track_item, '$.differences.departure[0]')) IS NOT NULL
                    AND SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', JSON_EXTRACT_SCALAR(track_item, '$.differences.departure[1]')) IS NOT NULL
                GROUP BY
                    p.care_stay_id, p.agency_id, p.customer_name, p.customer_city, 
                    p.arrival, p.departure, p.actual_duration_days, p.end_reason
            )
            SELECT
                dc.*,
                -- Calculate planned duration and reduction percentage
                DATE_DIFF(
                    DATE(SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', dc.first_change.original_departure)),
                    DATE(dc.arrival),
                    DAY
                ) as planned_duration_days,
                SAFE_DIVIDE(
                    DATE_DIFF(
                        DATE(SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', dc.first_change.original_departure)),
                        DATE(SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', dc.first_change.new_departure)),
                        DAY
                    ),
                    DATE_DIFF(
                        DATE(SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', dc.first_change.original_departure)),
                        DATE(dc.arrival),
                        DAY
                    )
                ) as reduction_percentage
            FROM departure_changes dc
            WHERE
                -- Was shortened (not extended)
                SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', dc.first_change.new_departure) < 
                SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', dc.first_change.original_departure)
                -- And shortened by more than 33%
                AND SAFE_DIVIDE(
                    DATE_DIFF(
                        DATE(SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', dc.first_change.original_departure)),
                        DATE(SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', dc.first_change.new_departure)),
                        DAY
                    ),
                    DATE_DIFF(
                        DATE(SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', dc.first_change.original_departure)),
                        DATE(dc.arrival),
                        DAY
                    )
                ) > 0.33
        )
        SELECT * FROM early_termination_details
        ORDER BY departure DESC
        """
        
        # Calculate date range
        start_date, end_date = query_manager._calculate_date_range(time_period)
        
        # Execute query
        from ..utils.bigquery_connection import BigQueryConnection
        connection = BigQueryConnection()
        results = connection.execute_query(query, {
            "agency_id": agency_id,
            "start_date": start_date,
            "end_date": end_date
        })
        
        # Format results
        details = []
        agency_name = "Unknown"
        
        for row in results:
            if not agency_name or agency_name == "Unknown":
                agency_name = row.get("agency_name", "Unknown")
                
            # Helper function to format dates
            def format_date(date_value):
                if not date_value:
                    return None
                if hasattr(date_value, 'isoformat'):
                    return date_value.isoformat()
                return str(date_value)
            
            detail = {
                "care_stay_id": row.get("care_stay_id"),
                "customer_name": row.get("customer_name"),
                "customer_city": row.get("customer_city"),
                "arrival": format_date(row.get("arrival")),
                "departure": format_date(row.get("departure")),
                "actual_duration_days": row.get("actual_duration_days"),
                "planned_duration_days": row.get("planned_duration_days"),
                "reduction_percentage": round(row.get("reduction_percentage", 0) * 100, 1) if row.get("reduction_percentage") else 0,
                "end_reason": row.get("end_reason")
            }
            details.append(detail)
        
        # Group by month (based on departure date)
        from collections import defaultdict
        grouped_by_month = defaultdict(list)
        
        for detail in details:
            if detail["departure"]:
                month_key = detail["departure"][:7]  # YYYY-MM
                grouped_by_month[month_key].append(detail)
        
        # Convert to sorted list
        grouped_data = []
        for month in sorted(grouped_by_month.keys(), reverse=True):
            grouped_data.append({
                "month": month,
                "count": len(grouped_by_month[month]),
                "terminations": grouped_by_month[month]
            })
        
        result = {
            "agency_id": agency_id,
            "agency_name": agency_name,
            "time_period": time_period,
            "total_count": len(details),
            "grouped_by_month": grouped_data
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch early termination details: {str(e)}")


# Include other routers if necessary
# from . import other_router
# router.include_router(other_router.router)