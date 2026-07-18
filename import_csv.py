"""
import_csv.py
One-time helper: loads your old movies.csv into the new SQLite database.

Run once, locally, before you deploy:

    python import_csv.py movies.csv
"""

import sys
import csv

from models import init_db, get_conn


def main(csv_path: str):
    init_db()
    count = 0
    with open(csv_path, newline="", encoding="utf-8") as f, get_conn() as conn:
        reader = csv.DictReader(f)
        for row in reader:
            title = row["movie"].strip().lower()
            rating_sum = float(row["rating"])
            votes = int(float(row["votes"]))  # tolerate "3" or "3.0" in the source CSV

            conn.execute(
                """
                INSERT INTO movies (title, rating_sum, votes) VALUES (?, ?, ?)
                ON CONFLICT(title) DO UPDATE SET rating_sum = excluded.rating_sum,
                                                  votes = excluded.votes
                """,
                (title, rating_sum, votes),
            )
            count += 1

    print(f"Imported {count} movies from {csv_path}.")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "movies.csv"
    main(path)
