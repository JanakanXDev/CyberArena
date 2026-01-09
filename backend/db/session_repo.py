from backend.db.database import get_connection


def create_session(user_id: int, curriculum_name: str) -> int:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO sessions (user_id, curriculum_name) VALUES (?, ?)",
        (user_id, curriculum_name)
    )
    conn.commit()

    session_id = cur.lastrowid
    conn.close()
    return session_id
