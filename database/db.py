import sqlite3
import json
import os

# data 폴더가 없으면 자동 생성
os.makedirs("data", exist_ok=True)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "worktracker.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            date TEXT NOT NULL,
            title TEXT,
            content TEXT NOT NULL,
            keywords TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS work (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            progress INTEGER DEFAULT 0,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


# ── History ───────────────────────────────────────────────

def add_history(type_, date, title, content, keywords="[]"):
    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO history (type, date, title, content, keywords) VALUES (?,?,?,?,?)",
            (type_, date, title, content, keywords)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[DB 오류] add_history 실패: {e}")
        return False


def get_history(year=None, month=None, type_=None):
    try:
        conn = get_connection()
        query = "SELECT * FROM history WHERE 1=1"
        params = []
        if year:
            query += " AND strftime('%Y', date) = ?"
            params.append(str(year))
        if month:
            query += " AND strftime('%m', date) = ?"
            params.append(str(month).zfill(2))
        if type_:
            query += " AND type = ?"
            params.append(type_)
        query += " ORDER BY date DESC"
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[DB 오류] get_history 실패: {e}")
        return []


def delete_history(id_):
    try:
        conn = get_connection()
        conn.execute("DELETE FROM history WHERE id = ?", (id_,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[DB 오류] delete_history 실패: {e}")
        return False


# ── Work ──────────────────────────────────────────────────

def add_work(title, status, start_date, end_date, progress, description):
    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO work (title, status, start_date, end_date, progress, description) VALUES (?,?,?,?,?,?)",
            (title, status, start_date, end_date, progress, description)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[DB 오류] add_work 실패: {e}")
        return False


def get_work(status=None):
    try:
        conn = get_connection()
        query = "SELECT * FROM work WHERE 1=1"
        params = []
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY start_date"
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[DB 오류] get_work 실패: {e}")
        return []


def update_work(id_, title, status, start_date, end_date, progress, description):
    try:
        conn = get_connection()
        conn.execute(
            "UPDATE work SET title=?, status=?, start_date=?, end_date=?, progress=?, description=? WHERE id=?",
            (title, status, start_date, end_date, progress, description, id_)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[DB 오류] update_work 실패: {e}")
        return False


def delete_work(id_):
    try:
        conn = get_connection()
        conn.execute("DELETE FROM work WHERE id = ?", (id_,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[DB 오류] delete_work 실패: {e}")
        return False
        