import strawberry

@strawberry.type
class NoteType:
    id: int
    name: str
    description: str

@strawberry.type
class NoteInput:
    name: str
    description: str