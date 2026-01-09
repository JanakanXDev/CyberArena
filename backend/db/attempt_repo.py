from backend.db.database import get_connection


def save_attempt(session_id: int, scenario_id: str, result: dict):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO attempts (session_id, scenario_id, score, risk, turns, outcome)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            session_id,
            scenario_id,
            result["score"],
            result["risk"],
            result["turns"],
            result["outcome"]
        )
    )

    conn.commit()
    conn.close()
