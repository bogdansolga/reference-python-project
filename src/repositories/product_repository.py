from lib.db import get_db


def _row_to_dict(row) -> dict | None:
    if row is None:
        return None
    return dict(row)


def find_all() -> list[dict]:
    db = get_db()
    rows = db.execute("SELECT * FROM products").fetchall()
    return [dict(row) for row in rows]


def find_by_id(id: int) -> dict | None:
    db = get_db()
    row = db.execute("SELECT * FROM products WHERE id = ?", (id,)).fetchone()
    return _row_to_dict(row)


def create(name: str, price: float, section_id: int) -> dict:
    db = get_db()
    cursor = db.execute(
        "INSERT INTO products (name, price, section_id) VALUES (?, ?, ?)",
        (name, price, section_id),
    )
    db.commit()
    return find_by_id(cursor.lastrowid)


def update(
    id: int,
    name: str | None = None,
    price: float | None = None,
    section_id: int | None = None,
) -> dict | None:
    db = get_db()
    current = find_by_id(id)
    if current is None:
        return None
    new_name = name if name is not None else current["name"]
    new_price = price if price is not None else current["price"]
    new_section_id = section_id if section_id is not None else current["section_id"]
    db.execute(
        "UPDATE products SET name = ?, price = ?, section_id = ? WHERE id = ?",
        (new_name, new_price, new_section_id, id),
    )
    db.commit()
    return find_by_id(id)


def delete(id: int) -> None:
    db = get_db()
    db.execute("DELETE FROM products WHERE id = ?", (id,))
    db.commit()
