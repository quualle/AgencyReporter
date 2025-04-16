"""
Agency listing and details queries.
These queries retrieve information about agencies from BigQuery.
"""

# Query to get all agencies
GET_ALL_AGENCIES = """
SELECT 
    _id AS agency_id,
    name AS agency_name
FROM 
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies`
ORDER BY 
    name ASC
"""

# Query to get details for a specific agency
GET_AGENCY_DETAILS = """
SELECT 
    _id AS agency_id,
    name AS agency_name,
    created_at,
    status
FROM 
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.agencies`
WHERE 
    _id = @agency_id
"""