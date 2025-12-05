from lib.db import get_db


def _row_to_dict(row) -> dict | None:
    if row is None:
        return None
    return dict(row)


def find_all() -> list[dict]:
    db = get_db()
    rows = db.execute("SELECT * FROM sections").fetchall()
    return [dict(row) for row in rows]


def find_by_id(id: int) -> dict | None:
    db = get_db()
    row = db.execute("SELECT * FROM sections WHERE id = ?", (id,)).fetchone()
    return _row_to_dict(row)


def create(name: str) -> dict:
    db = get_db()
    cursor = db.execute("INSERT INTO sections (name) VALUES (?)", (name,))
    db.commit()
    return find_by_id(cursor.lastrowid)


def update(id: int, name: str) -> dict | None:
    db = get_db()
    db.execute("UPDATE sections SET name = ? WHERE id = ?", (name, id))
    db.commit()
    return find_by_id(id)


def delete(id: int) -> None:
    db = get_db()
    db.execute("DELETE FROM sections WHERE id = ?", (id,))
    db.commit()
