import os
import sqlite3

_connection: sqlite3.Connection | None = None


def get_db() -> sqlite3.Connection:
    global _connection
    if _connection is None:
        db_path = os.environ.get("DATABASE_PATH", "sqlite.db")
        _connection = sqlite3.connect(db_path, check_same_thread=False)
        _connection.row_factory = sqlite3.Row
    return _connection


def close_db() -> None:
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None


def init_db() -> None:
    conn = get_db()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            price REAL NOT NULL,
            section_id INTEGER NOT NULL REFERENCES sections(id)
        );
        """
    )
    conn.commit()


def seed_db() -> None:
    """Seed database with initial data if empty."""
    conn = get_db()

    # Check if sections exist (idempotent)
    existing = conn.execute("SELECT COUNT(*) FROM sections").fetchone()[0]
    if existing > 0:
        return

    # Insert sections
    conn.execute("INSERT INTO sections (name) VALUES ('Electronics')")
    conn.execute("INSERT INTO sections (name) VALUES ('Books')")
    conn.execute("INSERT INTO sections (name) VALUES ('Clothing')")

    # Get section IDs
    electronics_id = conn.execute("SELECT id FROM sections WHERE name = 'Electronics'").fetchone()[0]
    books_id = conn.execute("SELECT id FROM sections WHERE name = 'Books'").fetchone()[0]
    clothing_id = conn.execute("SELECT id FROM sections WHERE name = 'Clothing'").fetchone()[0]

    # Insert products
    conn.execute("INSERT INTO products (name, price, section_id) VALUES ('Laptop', 999.99, ?)", (electronics_id,))
    conn.execute("INSERT INTO products (name, price, section_id) VALUES ('Smartphone', 699.99, ?)", (electronics_id,))
    conn.execute("INSERT INTO products (name, price, section_id) VALUES ('TypeScript Handbook', 29.99, ?)", (books_id,))
    conn.execute("INSERT INTO products (name, price, section_id) VALUES ('Clean Code', 39.99, ?)", (books_id,))
    conn.execute("INSERT INTO products (name, price, section_id) VALUES ('T-Shirt', 19.99, ?)", (clothing_id,))

    conn.commit()
