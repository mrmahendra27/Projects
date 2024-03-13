import strawberry

from Service.note import NoteService
from schema import NoteInput, NoteType


@strawberry.type
class Mutation:

    @strawberry.mutation
    async def add_note(self, note_data: NoteInput) -> NoteType:
        return await NoteService.add_note(note_data)

    @strawberry.mutation
    async def update_note(self, id: int, note_data: NoteInput) -> str:
        return await NoteService.update_note(id, note_data)

    @strawberry.mutation
    async def delete_note(self, id: int) -> str:
        return await NoteService.delete_note(id)
