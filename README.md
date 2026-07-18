# The Rating Room

A Flask web app for tracking movie ratings, backed by a real SQLite
database, production-ready to deploy to a free host.

## Local setup

```bash
pip install -r requirements.txt
cp .env.example .env        # edit if you want a custom SECRET_KEY
python app.py
```

Open **http://127.0.0.1:5000**.

If you have an old `movies.csv` from the CLI version, import it once:

```bash
python import_csv.py movies.csv
```

## Running it like production

```bash
pip install gunicorn
gunicorn app:app
```

This is what your hosting platform runs — `python app.py` is for local
dev only.

## Deploying for free

### Option 1: Render (easiest)
1. Push this folder to a GitHub repo.
2. Create a new Web Service on Render and connect that repo.
3. Set the build command to: `pip install -r requirements.txt`
4. Set the start command to: `gunicorn app:app`
5. Add an environment variable named `SECRET_KEY` with any random string.
6. Deploy and Render will give you a public URL such as `https://your-app.onrender.com`.

### Option 2: PythonAnywhere
1. Create a PythonAnywhere account.
2. Upload this project or clone it from GitHub.
3. Create a virtual environment and install the requirements.
4. Run the app with `gunicorn app:app` or use the web app configuration.

### Important note about the database
This app uses SQLite, so the database file is stored on disk with the project.
On free hosts, that file may be reset after deploys or restarts. That is fine for a demo or personal project. For a production app that must keep data forever, use a managed database such as PostgreSQL.

## Project structure

```
movie_webapp/
├── app.py            # Flask routes + app config
├── models.py         # sqlite3 database layer
├── import_csv.py     # one-time CSV → DB migration
├── movies.csv         # your old CLI data (optional)
├── Procfile           # tells the host how to start the app
├── requirements.txt
├── .env.example
├── templates/
└── static/
```
