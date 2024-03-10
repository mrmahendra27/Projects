from schema import NoteType, NoteInput
from ..Model.note import Note
from ..Repository.note import NoteRespository


class NoteService:

    @staticmethod
    async def add_note(note_data: NoteInput):
        note = Note()
        note.name = note_data.name
        note.description = note_data.description

        await NoteRespository.create(note)
        return {
            "message": "Note has been created!",
            "data": NoteType(id=note.id, name=note.name, description=note.description),
        }

    @staticmethod
    async def get_notes():
        notes = await NoteRespository.get_all()
        return {
            "data": [
                NoteType(id=note.id, name=note.name, description=note.description)
                for note in notes
            ]
        }

    @staticmethod
    async def get_note(id: int):
        note = await NoteRespository.get_by_id(id)
        return {
            "data": NoteType(id=note.id, name=note.name, description=note.description)
        }

    @staticmethod
    async def update_note(id: int, note_data: NoteInput):
        note = Note()
        note.id = id
        note.name = note_data.name
        note.description = note_data.description

        await NoteRespository.update(id, note)
        return {
            "message": "Note has been updated!",
            "data": NoteType(id=note.id, name=note.name, description=note.description),
        }

    @staticmethod
    async def delete_note(id: int):
        await NoteRespository.delete(id)
        return {
            "message": f"Note ID({id}) has been deleted!",
        }
