from ..Model.note import Note
from config import db

from sqlalchemy.sql import select
from sqlalchemy import update as sql_update, delete as sql_delete


class NoteRespository:

    @staticmethod
    async def create(note_data: Note):
        async with db as session:
            async with session.begin() as conn:
                await conn.add(note_data)
            await db.commit_rollback()

    @staticmethod
    async def get_by_id(id: int):
        async with db as session:
            statement = select(Note).where(Note.id == id)
            result = await session.execute(statement)
            return result.scalars.first()

    @staticmethod
    async def get_all():
        async with db as session:
            statement = select(Note)
            result = await session.execute(statement)
            return result.scalars.all()

    @staticmethod
    async def update(id: int, note_data: Note):
        async with db as session:
            statement = select(Note).where(Note.id == id)
            result = await session.execute(statement)
            note = result.scalars.first()

            note.name = note_data.name
            note.description = note_data.description

            query = (
                sql_update(Note)
                .where(Note.id == id)
                .values(**note.dict())
                .execution_options(synchronize_session=True)
            )

            await session.execute(query)
            await db.commit_rollback()

    @staticmethod
    async def delete(id: int):
        async with db as session:
            query = (
                sql_delete(Note)
                .where(Note.id == id)
                .execution_options(synchronize_session=True)
            )
            await session.execute(query)
            await db.commit_rollback()
