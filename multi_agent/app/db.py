import sqlite3

DB_PATH = "   "

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wallet_id TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wallet_id TEXT NOT NULL,
        post_id INTEGER NOT NULL,
        comment TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(post_id) REFERENCES posts(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        is_like BOOLEAN NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(post_id) REFERENCES posts(id)
    );
    """)

    conn.commit()
    conn.close()

def insert_post(content: str, wallet_id: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO posts (wallet_id, content) VALUES (?, ?)",
        (wallet_id, content)
    )
    conn.commit()
    post_id = cursor.lastrowid
    conn.close()
    return post_id

def insert_comment(comment: str, wallet_id: str, post_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO comments (wallet_id, post_id, comment) VALUES (?, ?, ?)",
        (wallet_id, post_id, comment)
    )
    conn.commit()
    conn.close()

def insert_like(post_id: str, is_like: bool):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO likes (post_id, is_like) VALUES (?, ?)",
        (post_id, is_like)
    )
    conn.commit()
    conn.close()
