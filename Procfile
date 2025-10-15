web: gunicorn app.web.server:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
worker: python scripts/migrate_db.py && python -m app.bot.main
