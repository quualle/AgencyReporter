"""
LLM analysis queries.
These queries retrieve communications data that will be analyzed by LLMs
to categorize reasons for cancellations and quality issues.
"""

# Query to get communications for cancellation analysis
GET_CANCELLATION_COMMUNICATIONS = """
-- Retrieve communications related to cancellations
-- This is a template and will be updated with the actual query
SELECT 
    -- Fields like communication_id, message, date will go here
FROM 
    -- Relevant tables will be joined here
WHERE 
    -- Conditions like agency_id, cancellation status, and date range will go here
"""

# Query to get communications for profile quality analysis
GET_PROFILE_QUALITY_COMMUNICATIONS = """
-- Retrieve communications related to profile quality issues
-- This is a template and will be updated with the actual query
"""

# Additional LLM analysis queries will be added here as they are provided