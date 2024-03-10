import os

from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


class DatabaseSession:
    def __init__(self, url: str = DATABASE_URL) -> None:
        # Create an Async database connection
        self.engine = create_async_engine(url, echo=True)
        # create a session local to interact with the database
        self.SessionLocal = sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )

    # Adding Tables/Models into a database
    async def create_all(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    # Dropping all Tables/Models from the database
    async def drop_all(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)

    # Closing the active database connection
    async def close(self):
        await self.engine.dispose()

    # Create a new session context for performing operations
    async def __aenter__(self) -> AsyncSession:
        self.session = self.SessionLocal()
        return self.session

    # Closes the session connection along with transactions(in progress) and ORM objects
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    # Commit/Rollback the transaction
    async def commit_rollback(self):
        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise


db = DatabaseSession()
