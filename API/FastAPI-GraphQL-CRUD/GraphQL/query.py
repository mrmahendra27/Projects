import strawberry

from typing import List
from schema import NoteType
from Service.note import NoteService


@strawberry.type
class Query:

    @strawberry.field
    def home(self) -> str:
        return "Welcome User!"

    @strawberry.field
    async def get_notes(self) -> List[NoteType]:
        return await NoteService.get_notes()

    @strawberry.field
    async def get_note(self, id: int) -> NoteType:
        return await NoteService.get_note(id)
