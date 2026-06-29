"""Backfill NULL trigger_score/industry_score/employee_score to 0."""
import sqlite3
conn = sqlite3.connect("prospectos.db")
cur = conn.cursor()
cur.execute("UPDATE companies SET trigger_score = COALESCE(trigger_score, 0), industry_score = COALESCE(industry_score, 0), employee_score = COALESCE(employee_score, 0)")
affected = cur.rowcount
conn.commit()
conn.close()
print(f"Backfilled {affected} companies")
