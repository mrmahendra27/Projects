import strawberry

from schema import NoteType
from Service.note import NoteService

@strawberry.type
class Query:

    @strawberry.field
    def home(self) -> str:
        return "Welcome User!"

    @strawberry.field
    async def get_notes(self):
        return await NoteService.get_notes()

    @strawberry.field
    async def get_note(self, id: int):
        return await NoteService.get_note(id)
