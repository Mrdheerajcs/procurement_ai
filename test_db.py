from database import execute_sql_query

DB_URL = 'postgresql://mmudevdb:mmudevdb@103.133.215.182:1506/Procurement'

query = """
SELECT *
FROM mpr_header
LIMIT 5
"""

df = execute_sql_query(query, DB_URL)

print(df)