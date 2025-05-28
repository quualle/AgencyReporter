from fastapi import APIRouter, Query, Depends
from typing import Optional
from datetime import datetime, timedelta

from app.queries.care_stays.confirmed_stays import execute_confirmed_stays_query
from app.utils.cache_decorator import cache_endpoint

router = APIRouter(
    tags=["care_stays"]
)


def get_date_range(time_period: str) -> tuple:
    """
    Berechnet Start- und Enddatum basierend auf dem Zeitraum.
    
    Args:
        time_period: Zeitraum (last_quarter, last_month, last_year, all_time)
        
    Returns:
        Tuple mit (start_date, end_date) im Format YYYY-MM-DD
    """
    today = datetime.now()
    
    if time_period == "last_month":
        # Letzter Monat
        if today.month == 1:
            start_date = datetime(today.year - 1, 12, 1)
        else:
            start_date = datetime(today.year, today.month - 1, 1)
        end_date = datetime(today.year, today.month, 1) - timedelta(days=1)
    
    elif time_period == "last_quarter":
        # Letztes Quartal
        current_quarter = (today.month - 1) // 3 + 1
        if current_quarter == 1:
            # Q4 des Vorjahres
            start_date = datetime(today.year - 1, 10, 1)
            end_date = datetime(today.year - 1, 12, 31)
        else:
            # Vorheriges Quartal des aktuellen Jahres
            start_month = (current_quarter - 2) * 3 + 1
            start_date = datetime(today.year, start_month, 1)
            if current_quarter == 2:
                end_date = datetime(today.year, 3, 31)
            elif current_quarter == 3:
                end_date = datetime(today.year, 6, 30)
            else:  # current_quarter == 4
                end_date = datetime(today.year, 9, 30)
    
    elif time_period == "last_year":
        # Letztes Jahr
        start_date = datetime(today.year - 1, 1, 1)
        end_date = datetime(today.year - 1, 12, 31)
    
    else:  # all_time
        # Alle verfügbaren Daten
        start_date = datetime(2020, 1, 1)
        end_date = today
    
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")


@router.get("/confirmed")
@cache_endpoint(ttl_hours=24, key_params=['time_period', 'agency_id'], cache_key_prefix="/care_stays/confirmed")
async def get_confirmed_stays(
    time_period: str = Query("last_quarter", regex="^(last_quarter|last_month|last_year|all_time)$"),
    agency_id: Optional[str] = Query(None, description="Filter by agency ID")
):
    """
    Gibt die Anzahl der bestätigten Care Stays pro Agentur zurück.
    
    - **time_period**: Zeitraum für die Analyse (last_quarter, last_month, last_year, all_time)
    - **agency_id**: Optional - Filter für eine spezifische Agentur
    
    Returns:
        Liste mit Agenturen und deren bestätigten Care Stays inkl. Ranking
    """
    try:
        # Datumsbereiche bestimmen
        start_date, end_date = get_date_range(time_period)
        
        # Query ausführen
        results = execute_confirmed_stays_query(start_date, end_date, agency_id)
        
        # Gesamtsumme berechnen
        total_confirmed = sum(agency['confirmed_stays_count'] for agency in results)
        
        return {
            "time_period": time_period,
            "start_date": start_date,
            "end_date": end_date,
            "total_confirmed_stays": total_confirmed,
            "agency_count": len(results),
            "agencies": results
        }
        
    except Exception as e:
        raise Exception(f"Fehler beim Abrufen der bestätigten Care Stays: {str(e)}")