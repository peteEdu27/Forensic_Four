"""Week 11: three questions against data/case.db.
Run (after python -m src.fetch_city): python -m src.queries"""
import sqlite3, pandas as pd
con = sqlite3.connect("data/case.db")

q1 = """SELECT servyr AS year, COUNT(*) AS murders
        FROM incidents WHERE servyr BETWEEN 2014 AND 2026
        GROUP BY servyr ORDER BY servyr"""

q2 = """SELECT beat, COUNT(*) AS n FROM incidents
        WHERE beat IS NOT NULL GROUP BY beat ORDER BY n DESC LIMIT 5"""

# our squad's slice: murders on a residential premise
q3 = """SELECT ROUND(100.0 * SUM(premise LIKE '%RESIDENCE%') / COUNT(*), 1) AS pct_residence
        FROM incidents"""

for q in (q1, q2, q3):
    print(pd.read_sql(q, con), "\n")
