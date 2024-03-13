from schema import NoteType, NoteInput
from Model.note import Note
from Repository.note import NoteRespository
from typing import List


class NoteService:

    @staticmethod
    async def add_note(note_data: NoteInput) -> NoteType:
        note = Note()
        note.name = note_data.name
        note.description = note_data.description

        await NoteRespository.create(note)
        return NoteType(id=note.id, name=note.name, description=note.description)

    @staticmethod
    async def get_notes() -> List[NoteType]:
        notes = await NoteRespository.get_all()
        return [
            NoteType(id=note.id, name=note.name, description=note.description)
            for note in notes
        ]

    @staticmethod
    async def get_note(id: int) -> NoteType:
        note = await NoteRespository.get_by_id(id)
        return NoteType(id=note.id, name=note.name, description=note.description)

    @staticmethod
    async def update_note(id: int, note_data: NoteInput) -> str:
        note = Note()
        note.id = id
        note.name = note_data.name
        note.description = note_data.description

        await NoteRespository.update(id, note)
        return f"Note ID({id}) has been updated!"

    @staticmethod
    async def delete_note(id: int) -> str:
        await NoteRespository.delete(id)
        return f"Note ID({id}) has been deleted!"
