from sqlalchemy import text

from apps.api.app.db.session import engine


def check_database() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
