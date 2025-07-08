import psycopg2

def create_database_if_not_exists(dbname, user, password, host, port="5432"):
    # Always connect to the default 'postgres' DB
    conn = psycopg2.connect(dbname="postgres", user=user, password=password, host=host, port=port)
    conn.autocommit = True
    cur = conn.cursor()

    # Check if the database already exists
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (dbname,))
    exists = cur.fetchone()

    if not exists:
        try:
            cur.execute(f'CREATE DATABASE "{dbname}";')  # Use double quotes for case sensitivity
        except psycopg2.errors.DuplicateDatabase:
            pass
    else:
        pass

    cur.close()
    conn.close()