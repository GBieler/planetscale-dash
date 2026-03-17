#!/usr/bin/env python3
"""
Connect to PlanetScale (PostgreSQL) and run queries from queries.py.
Loads PSQL_PASSWORD from .env, or set in environment.

Usage:
    python query_workflow_db.py --list              # List available queries
    python query_workflow_db.py usage_data          # Run a specific query
    python query_workflow_db.py query1 query2       # Run multiple queries
    python query_workflow_db.py --all               # Run all queries
"""

import argparse
import csv
import os
import sys

import psycopg2

from dotenv import load_dotenv

from queries import QUERIES

load_dotenv()


def run_query(conn, name, query_def):
    out_path = query_def["out_path"]
    query = query_def["query"]
    params = query_def.get("params")

    print(f"Running query: {name}")
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
            print(f"  Saved {len(rows)} row(s) to {out_path}")
        else:
            conn.commit()
            print(f"  Done. Rows affected: {cur.rowcount}")


def list_queries():
    print("Available queries:")
    for name, query_def in QUERIES.items():
        out_path = query_def["out_path"]
        output_type = f"-> {out_path}" if out_path else "(no output file)"
        print(f"  {name:25} {output_type}")


def main():
    parser = argparse.ArgumentParser(
        description="Run named queries against PlanetScale database."
    )
    parser.add_argument(
        "queries",
        nargs="*",
        help="Name(s) of the query to run (see --list for available queries)",
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all available queries and exit",
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Run all queries",
    )
    args = parser.parse_args()

    if args.list:
        list_queries()
        sys.exit(0)

    if not args.queries and not args.all:
        parser.print_help()
        print("\nUse --list to see available queries.")
        sys.exit(1)

    if args.all:
        queries_to_run = list(QUERIES.keys())
    else:
        queries_to_run = args.queries
        for name in queries_to_run:
            if name not in QUERIES:
                print(f"Error: Unknown query '{name}'", file=sys.stderr)
                print("Use --list to see available queries.", file=sys.stderr)
                sys.exit(1)

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
        for name in queries_to_run:
            run_query(conn, name, QUERIES[name])
    finally:
        conn.close()


if __name__ == "__main__":
    main()
