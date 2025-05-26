from app.utils.bigquery_connection import BigQueryConnection

# Test query to see table structure
query = """
SELECT 
    cs.*,
    c.customer_name,
    c.customer_city
FROM 
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.care_stays` cs
JOIN 
    `gcpxbixpflegehilfesenioren.PflegehilfeSeniore_BI.contracts` c ON cs.contract_id = c._id
WHERE 
    c.agency_id = '668d1726356103192b2b6bed'
LIMIT 1
"""

connection = BigQueryConnection()
results = connection.execute_query(query)

if results:
    print("Available columns in care_stays:")
    for key in results[0].keys():
        print(f"  - {key}")
else:
    print("No results found")