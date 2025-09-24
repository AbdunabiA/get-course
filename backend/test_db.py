from sqlmodel import Session
from sqlalchemy import text  # 👈 import text()
from app.core.database import engine

with Session(engine) as session:
    result = session.exec(
        text("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
    )
    print(result.all())
