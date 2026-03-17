#!/usr/bin/env python3
"""
Connect to PlanetScale (PostgreSQL) and run SELECT on first 10 rows of workflow_db.
Loads PSQL_PASSWORD from .env, or set in environment, or pass --password.
"""

import csv
import os
import sys

import psycopg2

from dotenv import load_dotenv

from queries import QUERIES

load_dotenv()


def run_query(conn, out_path, query, params=None):
    with conn.cursor() as cur:
        if params is not None:
            cur.execute(query, params)
        else:
            cur.execute(query)
        if out_path is not None:
            rows = cur.fetchall()
            colnames = [desc[0] for desc in cur.description]
            with open(out_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(colnames)
                writer.writerows(rows)
            print(f"Saved {len(rows)} row(s) to {out_path}")
        else:
            conn.commit()
            print(f"Done. Rows affected: {cur.rowcount}")


def main():
    conn_params = {
        "host": os.environ.get("PSQL_HOST"),
        "port": os.environ.get("PSQL_PORT"),
        "user": os.environ.get("PSQL_USER"),
        "password": os.environ.get("PSQL_PASSWORD"),
        "dbname": os.environ.get("PSQL_DBNAME"),
        "sslmode": "require",
    }

    try:
        conn = psycopg2.connect(**conn_params)
    except Exception as e:
        print(f"Connection failed: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        for item in QUERIES:
            out_path, query = item[0], item[1]
            params = item[2] if len(item) >= 3 else None
            run_query(conn, out_path, query, params)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
