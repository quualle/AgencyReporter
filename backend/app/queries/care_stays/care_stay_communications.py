from typing import Dict, Any, List
from google.cloud import bigquery
from datetime import datetime

from ...utils.bigquery_connection import get_bigquery_client

async def get_communications_for_stay(care_stay_id: str) -> Dict[str, Any]:
    """
    Get all email and ticket communications related to a specific care stay
    """
    client = get_bigquery_client()
    
    # Get emails related to this care stay
    email_query = """
    SELECT 
        email_id,
        subject,
        body,
        sender,
        recipient,
        sent_date,
        sentiment,
        'email' as communication_type
    FROM 
        `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.customer_emails`
    WHERE 
        care_stay_id = @care_stay_id
        OR (customer_id = (
            SELECT customer_id 
            FROM `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` 
            WHERE care_stay_id = @care_stay_id
        ) AND sent_date BETWEEN (
            SELECT DATE_SUB(start_date, INTERVAL 7 DAY)
            FROM `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` 
            WHERE care_stay_id = @care_stay_id
        ) AND (
            SELECT DATE_ADD(IFNULL(end_date, CURRENT_DATE()), INTERVAL 14 DAY)
            FROM `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` 
            WHERE care_stay_id = @care_stay_id
        ))
    ORDER BY sent_date DESC
    """
    
    # Get tickets related to this care stay
    ticket_query = """
    SELECT 
        ticket_id,
        title as subject,
        description as body,
        created_by as sender,
        assigned_to as recipient,
        created_date as sent_date,
        priority as sentiment,
        'ticket' as communication_type
    FROM 
        `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.support_tickets`
    WHERE 
        care_stay_id = @care_stay_id
        OR (customer_id = (
            SELECT customer_id 
            FROM `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` 
            WHERE care_stay_id = @care_stay_id
        ) AND created_date BETWEEN (
            SELECT DATE_SUB(start_date, INTERVAL 7 DAY)
            FROM `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` 
            WHERE care_stay_id = @care_stay_id
        ) AND (
            SELECT DATE_ADD(IFNULL(end_date, CURRENT_DATE()), INTERVAL 14 DAY)
            FROM `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` 
            WHERE care_stay_id = @care_stay_id
        ))
    ORDER BY created_date DESC
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("care_stay_id", "STRING", care_stay_id)
        ]
    )
    
    # Execute both queries
    email_job = client.query(email_query, job_config=job_config)
    ticket_job = client.query(ticket_query, job_config=job_config)
    
    emails = []
    for row in email_job.result():
        emails.append({
            "id": row.email_id,
            "subject": row.subject,
            "body": row.body,
            "sender": row.sender,
            "recipient": row.recipient,
            "date": row.sent_date.isoformat() if row.sent_date else None,
            "sentiment": row.sentiment,
            "type": "email"
        })
    
    tickets = []
    for row in ticket_job.result():
        tickets.append({
            "id": row.ticket_id,
            "subject": row.subject,
            "body": row.body,
            "sender": row.sender,
            "recipient": row.recipient,
            "date": row.sent_date.isoformat() if row.sent_date else None,
            "sentiment": row.sentiment,
            "type": "ticket"
        })
    
    return {
        "emails": emails,
        "tickets": tickets,
        "total_count": len(emails) + len(tickets),
        "care_stay_id": care_stay_id
    }