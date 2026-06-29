"""Add missing columns to existing companies table.

Run: python migration_add_columns.py
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "prospectos.db")

COLUMNS = [
    ("trigger_score", "FLOAT"),
    ("industry_score", "FLOAT"),
    ("employee_score", "FLOAT"),
    ("recommended_action", "TEXT"),
    ("execution_plan", "TEXT"),
    ("prospect_intelligence", "TEXT"),
]

def run_migration():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}, skipping migration.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get existing columns
    cursor.execute("PRAGMA table_info(companies)")
    existing = {row[1] for row in cursor.fetchall()}

    for col_name, col_type in COLUMNS:
        if col_name not in existing:
            sql = f"ALTER TABLE companies ADD COLUMN {col_name} {col_type} NULL"
            cursor.execute(sql)
            print(f"Added column: {col_name} ({col_type})")
        else:
            print(f"Column already exists: {col_name}")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    run_migration()
