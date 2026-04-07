"""
Named queries and output paths.
Each entry: {"name": str, "out_path": str|None, "query": str, "params": tuple|None}
out_path None for UPDATE/INSERT/DELETE (no CSV).
For IN %s with a list of IDs, pass a tuple of the tuple, e.g. ((1, 2, 3),).
"""

QUERIES = {
    "workflow_billing_data": {
        "out_path": "workflow_billing_data.csv",
        "query": """
            SELECT DISTINCT ON (workflow_billing_db.id) project_db.team_id AS team_id, workflow_billing_db.id, workflow_billing_db.app_name, workflow_billing_db.start_time, workflow_billing_db.exit_time, workflow_billing_db.gpu
            FROM workflow_billing_db
            JOIN workflow_db ON workflow_db.modal_app_name = workflow_billing_db.app_name
            JOIN project_db ON project_db.id = workflow_db.project_id
            WHERE start_time > '2026-01-01 00:00:00'
            ORDER BY workflow_billing_db.id DESC, workflow_billing_db.start_time DESC
        """,
        "params": None,
    },
    "users_per_team": {
        "out_path": "users_per_team.csv",
        "query": """
            SELECT DISTINCT u.email, t.id AS team_id
            FROM user_db u
            JOIN teams_users tu ON u.id = tu.user_id
            JOIN team_db t ON tu.team_id = t.id
            ORDER BY t.id
        """,
        "params": None,
    },
    "new_subscribers": {
        "out_path": "new_subscribers.csv",
        "query": """
            SELECT u.email, p.type, t.id AS team_id, s.created_at
            FROM team_db t
            JOIN teams_users tu ON t.id = tu.team_id
            JOIN user_db u ON u.id = tu.user_id
            JOIN subscription_plan_db p ON p.id = t.subscription_plan_id
            JOIN stripe_billing_info_db s ON s.team_id = t.id
            WHERE s.status = 'ACTIVE'
              AND s.created_at >= DATE '2025-09-01'
              AND s.id IN %s
            ORDER BY s.created_at DESC
        """,
        "params": ((1974,1973,1972,1961,1975,1976,1978,1986,1988,1995,1996,1998,2000,2001),),  # list of stripe_billing_info_db.id
    },
    "update_billing_status": {
        "out_path": None,
        "query": """
            UPDATE workflow_billing_db
            SET billing_status = 'PAID'
            WHERE app_name IN (
                SELECT DISTINCT w.modal_app_name
                FROM workflow_db w
                JOIN project_db p ON w.project_id = p.id
                WHERE p.team_id IN %s
            )
            AND (exit_time <= %s OR exit_time is NULL)
            AND billing_status = 'PENDING'
        """,
        "params": ((3295,), "2026-03-30 11:40:43"),  # (team_ids_tuple, exit_time_cutoff)
    },
    "team_extract_user_stats": {
        "out_path": "team_extract_user_stats.csv",
        "query": """
            SELECT
                DATE(wh.created_at) AS date,
                u.email,
                w.name AS workflow,
                MIN(wh.created_at) AS start_time,
                COUNT(*) AS generation_count,
                SUM(wh.execution_time_seconds) AS total_generation_time_seconds
            FROM user_db u
            JOIN teams_users tu ON u.id = tu.user_id
            JOIN workflow_history_db wh ON u.auth_id = wh.auth_id
            JOIN workflow_db w ON wh.workflow_id = w.id
            WHERE tu.team_id = 3087
              AND w.project_id = 2919
            AND email NOT IN ('guillaume@viewcomfy.com', 'jean@viewcomfy.com')
            GROUP BY DATE(wh.created_at), u.email, w.name, w.GPU
            ORDER BY DATE(wh.created_at) DESC, u.email, w.name
        """,
        "params": None,
    },
    "billing_page_data": {
        "out_path": "billing_page_data.csv",
        "query": """
            SELECT
                project_db.name AS project_name,
                w.name AS workflow,
                wb.start_time,
                wb.exit_time,
                wb.gpu,
                (wb.exit_time - wb.start_time) AS duration,
                CASE
                    WHEN wb.gpu::text = 'T4' THEN EXTRACT(EPOCH FROM (wb.exit_time - wb.start_time)) * 0.000181
                    WHEN wb.gpu::text = 'L4' THEN EXTRACT(EPOCH FROM (wb.exit_time - wb.start_time)) * 0.000321
                    WHEN wb.gpu::text = 'A10G' THEN EXTRACT(EPOCH FROM (wb.exit_time - wb.start_time)) * 0.000612
                    WHEN wb.gpu::text = 'L40S' THEN EXTRACT(EPOCH FROM (wb.exit_time - wb.start_time)) * 0.000975
                    WHEN wb.gpu::text IN ('A100-40GB', 'A100_40GB') THEN EXTRACT(EPOCH FROM (wb.exit_time - wb.start_time)) * 0.00114
                    WHEN wb.gpu::text IN ('A100-80GB', 'A100_80GB') THEN EXTRACT(EPOCH FROM (wb.exit_time - wb.start_time)) * 0.001709
                    WHEN wb.gpu::text = 'H100' THEN EXTRACT(EPOCH FROM (wb.exit_time - wb.start_time)) * 0.002338
                    WHEN wb.gpu::text = 'H200' THEN EXTRACT(EPOCH FROM (wb.exit_time - wb.start_time)) * 0.002681
                    WHEN wb.gpu::text = 'B200' THEN EXTRACT(EPOCH FROM (wb.exit_time - wb.start_time)) * 0.0037
                    WHEN wb.gpu::text = 'CPU' THEN EXTRACT(EPOCH FROM (wb.exit_time - wb.start_time)) * 0.0000417
                    ELSE 0
                END AS cost
            FROM workflow_billing_db wb
            JOIN project_db ON wb.project_id = project_db.id
            JOIN team_db ON project_db.team_id = team_db.id
            JOIN workflow_db w ON wb.workflow_id = w.id
            WHERE team_db.id = %s
              AND wb.project_id = %s
              AND wb.start_time >= %s
              AND wb.exit_time <= %s
            ORDER BY wb.start_time ASC
        """,
        "params": (3087, 2919, "2026-02-20 00:00:00", "2026-04-01 23:59:59"),  # (team_id, project_id, start_time, end_time, limit)
    },
}
