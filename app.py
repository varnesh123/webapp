"""
app.py
Flask front-end for the movie ratings tracker.

Local dev:
    python app.py
Production (what the hosting platform runs):
    gunicorn app:app
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

from models import init_db, all_movies, add_rating, delete_movie, stats

app = Flask(__name__)

# Secret key comes from the environment in production; a local default so
# `python app.py` still works with zero setup.
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
app.config["JSON_SORT_KEYS"] = False

init_db()  # creates the movies table on first run; no-op after that


@app.route("/")
def index():
    query = request.args.get("q", "")
    sort_by = request.args.get("sort", "title")
    return render_template(
        "index.html",
        movies=all_movies(query=query, sort_by=sort_by),
        query=query,
        sort_by=sort_by,
        stats=stats(),
    )


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title", "").strip()
    rating_raw = request.form.get("rating", "").strip()

    if not title:
        flash("Movie title can't be empty.", "error")
        return redirect(url_for("index"))

    try:
        rating = float(rating_raw)
    except ValueError:
        flash("Rating has to be a number.", "error")
        return redirect(url_for("index"))

    if not (0 <= rating <= 10):
        flash("Rating has to be between 0 and 10.", "error")
        return redirect(url_for("index"))

    status = add_rating(title, rating)
    if status == "created":
        flash(f"Added '{title.title()}' to the list.", "success")
    else:
        flash(f"Added another vote for '{title.title()}'.", "success")

    return redirect(url_for("index"))


@app.route("/delete/<title>", methods=["POST"])
def delete(title):
    if delete_movie(title):
        flash(f"Removed '{title.title()}'.", "success")
    else:
        flash(f"Couldn't find '{title.title()}'.", "error")
    return redirect(url_for("index"))


@app.route("/api/search")
def api_search():
    query = request.args.get("q", "")
    sort_by = request.args.get("sort", "title")
    return jsonify(all_movies(query=query, sort_by=sort_by))


@app.route("/healthz")
def healthz():
    """Simple endpoint hosting platforms can ping to check the app is alive."""
    return {"status": "ok"}, 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
