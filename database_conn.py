import psycopg2
from http.server import HTTPServer, SimpleHTTPRequestHandler


conn = psycopg2.connect(
    host="200.10.150.106",
    database="papers_info",
    user="postgres",
    password="postgres")

print("Opened database successfully")
cursor = conn.cursor()
name1 = "Sheelagh"
name2 = "Carpendale"

querystring = "SELECT au.name, p.title FROM authors as au"
querystring += "  JOIN papers_authors as pa ON pa.authors_id = au.id"
querystring += "  JOIN papers as p ON p.id = pa.papers_id"
querystring += "  WHERE UPPER(au.name) LIKE '%" + name1.upper() + "%'"
querystring += "  AND UPPER(au.name) LIKE '%" + name2.upper() + "%' FETCH FIRST 10 ROWS ONLY"

cursor.execute(querystring)

print("Selecting rows from mobile table using cursor.fetchall")
mobile_records = cursor.fetchall()
for row in mobile_records:
    print(row)

print("Print each row and it's columns values")