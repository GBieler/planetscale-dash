"""
Named queries and output paths.
Each entry: (out_path, query_sql, params?) — out_path None for UPDATE/INSERT/DELETE (no CSV).
For IN %s with a list of IDs, pass a tuple of the tuple, e.g. ((1, 2, 3),).
"""

QUERIES = [
    # usage_data
    (
        "usage_data.csv",
        """SELECT DISTINCT ON (workflow_billing_db.id) project_db.team_id AS team_id, workflow_billing_db.id, workflow_billing_db.app_name, workflow_billing_db.start_time, workflow_billing_db.exit_time, workflow_billing_db.gpu
FROM workflow_billing_db
JOIN workflow_db ON workflow_db.modal_app_name = workflow_billing_db.app_name
JOIN project_db ON project_db.id = workflow_db.project_id
WHERE start_time > '2026-01-01 00:00:00'
ORDER BY workflow_billing_db.id DESC, workflow_billing_db.start_time DESC""",
        None,
    ),
    # users_per_team
    (
        "users_per_team.csv",
        """SELECT DISTINCT u.email, t.id AS team_id
FROM user_db u
JOIN teams_users tu ON u.id = tu.user_id
JOIN team_db t ON tu.team_id = t.id
ORDER BY t.id""",
        None,
    ),
    # new_subscribers — params: tuple of stripe_billing_info id ints, e.g. ((1, 2, 3),)
    (
        "new_subscribers.csv",
        """SELECT u.email, p.type, t.id AS team_id, s.created_at
FROM team_db t
JOIN teams_users tu ON t.id = tu.team_id
JOIN user_db u ON u.id = tu.user_id
JOIN subscription_plan_db p ON p.id = t.subscription_plan_id
JOIN stripe_billing_info_db s ON s.team_id = t.id
WHERE s.status = 'ACTIVE'
  AND s.created_at >= DATE '2025-09-01'
  AND s.id IN %s
ORDER BY s.created_at DESC""",
        ((1875, 1870, 1873, 1857, 1858, 1860, 1862, 1863),),  # list of stripe_billing_info_db.id
    ),
    # UPDATE billing status (no file output) — params: tuple of team_id ints, e.g. ((1, 2, 3),)
    (
        None,
        """UPDATE workflow_billing_db
SET billing_status = 'PAID'
WHERE app_name IN (
    SELECT DISTINCT w.modal_app_name
    FROM workflow_db w
    JOIN project_db p ON w.project_id = p.id
    WHERE p.team_id IN %s
)
AND (exit_time <= %s OR exit_time is NULL)
AND billing_status = 'PENDING'""",
        ((1482,2218,2664,3460,4181,4199,4333,), "2026-03-11 12:10:43"),  # (team_ids_tuple, exit_time_cutoff) 
    ),
]
