import psycopg2

DB_NAME = "otel_practice"
DB_USER = "auuntoo"
DB_PASS = "auuntoo"
DB_HOST = "postgres"
DB_PORT = "5432"

print("Initializing connection pool")
pg_client = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    port=DB_PORT
)
