from backend.db.database import get_connection
from backend.models.user import User, Role


def get_or_create_user(username: str, role: Role) -> User:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, username, role FROM users WHERE username = ?",
        (username,)
    )
    row = cur.fetchone()

    if row:
        conn.close()
        return User(id=row[0], username=row[1], role=Role[row[2]])

    cur.execute(
        "INSERT INTO users (username, role) VALUES (?, ?)",
        (username, role.name)
    )
    conn.commit()

    user_id = cur.lastrowid
    conn.close()

    return User(id=user_id, username=username, role=role)
