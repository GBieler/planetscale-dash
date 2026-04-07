# PlanetScale Query Runner

A simple CLI tool to store, manage, and run PlanetScale (PostgreSQL) queries from the terminal. Define your queries once in a Python file, then execute them by name—results are automatically exported to CSV, or for write operations, committed to the database.

## Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root with your database credentials:

```
PSQL_HOST=your-host.aws.neon.tech
PSQL_PORT=5432
PSQL_USER=your-username
PSQL_PASSWORD=your-password
PSQL_DBNAME=your-database
```

## Usage

### Running queries

```bash
# List all available queries
python query_workflow_db.py --list

# Run a specific query
python query_workflow_db.py <query_name>

# Run multiple queries
python query_workflow_db.py <query_name_1> <query_name_2>

# Run all queries
python query_workflow_db.py --all
```

### Adding queries

Add your queries to `queries.py`. Each query is a dictionary entry in the `QUERIES` dict with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `out_path` | `str` or `None` | Path to save CSV results. Use `None` for UPDATE/INSERT/DELETE queries. |
| `query` | `str` | The SQL query to execute. Use `%s` for parameterized values. |
| `params` | `tuple` or `None` | Parameters to pass to the query. Use `None` if no parameters. |

**Example SELECT query (exports to CSV):**

```python
"users_per_team": {
    "out_path": "users_per_team.csv",
    "query": """
        SELECT u.email, t.id AS team_id
        FROM user_db u
        JOIN teams_users tu ON u.id = tu.user_id
        JOIN team_db t ON tu.team_id = t.id
    """,
    "params": None,
},
```

**Example UPDATE query (no output file):**

```python
"update_status": {
    "out_path": None,
    "query": """
        UPDATE billing_db
        SET billing_status = 'PAID'
        WHERE team_id = %s
    """,
    "params": (123,),
},
```

**Using `IN` clauses with multiple values:**

For `IN %s` with a list of IDs, wrap the tuple in another tuple:

```python
"params": ((1, 2, 3, 4, 5),),  # Note the double parentheses
```
